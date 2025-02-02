# Import required libraries
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
import music21
import pygame
import tempfile
import os
import random
from google import genai


from dotenv import load_dotenv


load_dotenv()

# Create music directory if it doesn't exist
if not os.path.exists('music'):
    os.makedirs('music')


client = genai.Client(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model_id = "gemini-2.0-flash-exp"  # Changed to supported model name



class MusicState(TypedDict):
    """Define the structure of the state for the music generation workflow."""
    musician_input: str  
    melody: str         
    harmony: str         # Generated harmony
    rhythm: str          # Generated rhythm
    style: str           # Desired musical style
    composition: str     # Complete musical composition
    midi_file: str       # Path to the generated MIDI file


def melody_generator(state: MusicState) -> Dict:
    """Generate a melody based on the user's input."""
    prompt = ChatPromptTemplate.from_template(
        "Generate a melody based on this input: {input}. Represent it as a string of notes in music21 format."
    )
    response = client.models.generate_content(
        model=model_id,
        contents=f"Generate a melody based on this input: {state['musician_input']}. Represent it as a string of notes in music21 format."
    )
    return {"melody": response.text}

def harmony_creator(state: MusicState) -> Dict:
    """Create harmony for the generated melody."""
    prompt = ChatPromptTemplate.from_template(
        "Create harmony for this melody: {melody}. Represent it as a string of chords in music21 format."
    )
    response = client.models.generate_content(
        model=model_id,
        contents=f"Create harmony for this melody: {state['melody']}. Represent it as a string of chords in music21 format."
    )
    return {"harmony": response.text}

def rhythm_analyzer(state: MusicState) -> Dict:
    """Analyze and suggest a rhythm for the melody and harmony."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze and suggest a rhythm for this melody and harmony: {melody}, {harmony}. Represent it as a string of durations in music21 format."
    )
    response = client.models.generate_content(
        model=model_id,
        contents=f"Analyze and suggest a rhythm for this melody and harmony: {state['melody']}, {state['harmony']}. Represent it as a string of durations in music21 format."
    )
    return {"rhythm": response.text}

def style_adapter(state: MusicState) -> Dict:
    """Adapt the composition to the specified musical style."""
    prompt = ChatPromptTemplate.from_template(
        "Adapt this composition to the {style} style: Melody: {melody}, Harmony: {harmony}, Rhythm: {rhythm}. Provide the result in music21 format."
    )
    response = client.models.generate_content(
        model=model_id,
        contents=f"Adapt this composition to the {state['style']} style: Melody: {state['melody']}, Harmony: {state['harmony']}, Rhythm: {state['rhythm']}. Provide the result in music21 format."
    )
    return {"composition": response.text}

def midi_converter(state: MusicState) -> Dict:
    """Convert the composition to MIDI format and save it as a file."""
    # Create a new stream
    piece = music21.stream.Score()

    # Add the composition description to the stream as a text expression
    description = music21.expressions.TextExpression(state["composition"])
    piece.append(description)

    # Define instruments for Lofi style
    instruments = {
        'piano': music21.instrument.Piano(),
        'guitar': music21.instrument.ElectricGuitar(),
        'synth': music21.instrument.ElectricOrgan(),  # Using organ as synth substitute
    }

    # Define a wide variety of scales and chords
    scales = {
        'C major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'C minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
        'C harmonic minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B'],
        'C melodic minor': ['C', 'D', 'Eb', 'F', 'G', 'A', 'B'],
        'C dorian': ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb'],
        'C phrygian': ['C', 'Db', 'Eb', 'F', 'G', 'Ab', 'Bb'],
        'C lydian': ['C', 'D', 'E', 'F#', 'G', 'A', 'B'],
        'C mixolydian': ['C', 'D', 'E', 'F', 'G', 'A', 'Bb'],
        'C locrian': ['C', 'Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb'],
        'C whole tone': ['C', 'D', 'E', 'F#', 'G#', 'A#'],
        'C diminished': ['C', 'D', 'Eb', 'F', 'Gb', 'Ab', 'A', 'B'],
    }

    chords = {
        'C major': ['C4', 'E4', 'G4'],
        'C minor': ['C4', 'Eb4', 'G4'],
        'C diminished': ['C4', 'Eb4', 'Gb4'],
        'C augmented': ['C4', 'E4', 'G#4'],
        'C dominant 7th': ['C4', 'E4', 'G4', 'Bb4'],
        'C major 7th': ['C4', 'E4', 'G4', 'B4'],
        'C minor 7th': ['C4', 'Eb4', 'G4', 'Bb4'],
        'C half-diminished 7th': ['C4', 'Eb4', 'Gb4', 'Bb4'],
        'C fully diminished 7th': ['C4', 'Eb4', 'Gb4', 'A4'],
    }

    def create_melody(scale_name, duration, instrument):
        """Create a melody based on a given scale with specified instrument."""
        melody = music21.stream.Part()
        melody.insert(0, instruments[instrument])
        scale = scales[scale_name]
        for _ in range(duration):
            note = music21.note.Note(random.choice(scale) + '4')
            note.quarterLength = 1
            melody.append(note)
        return melody

    def create_chord_progression(duration, instrument):
        """Create a chord progression with specified instrument."""
        harmony = music21.stream.Part()
        harmony.insert(0, instruments[instrument])
        for _ in range(duration):
            chord_name = random.choice(list(chords.keys()))
            chord = music21.chord.Chord(chords[chord_name])
            chord.quarterLength = 1
            harmony.append(chord)
        return harmony

    # Parse the user input to determine scale and style
    user_input = state['musician_input'].lower()
    if 'minor' in user_input:
        scale_name = 'C minor'
    elif 'major' in user_input:
        scale_name = 'C major'
    else:
        scale_name = random.choice(list(scales.keys()))

    # Create an 8-bar piece with multiple instruments
    piano_melody = create_melody(scale_name, 7, 'piano')
    guitar_harmony = create_chord_progression(7, 'guitar')
    synth_pad = create_chord_progression(7, 'synth')

    # Add final notes/chords
    final_note = music21.note.Note(scales[scale_name][0] + '4')
    final_note.quarterLength = 1
    piano_melody.append(final_note)
    
    final_chord = music21.chord.Chord(chords[scale_name.split()[0] + ' ' + scale_name.split()[1]])
    final_chord.quarterLength = 1
    guitar_harmony.append(final_chord)
    synth_pad.append(final_chord)

    # Add all parts to the piece
    piece.append(piano_melody)
    piece.append(guitar_harmony)
    piece.append(synth_pad)

    # Set the tempo to 60 BPM
    piece.insert(0, music21.tempo.MetronomeMark(number=60))

    # Create files in music directory
    midi_path = os.path.join('music', f'composition_{random.randint(1000,9999)}.mid')
    piece.write('midi', midi_path)
        
    return {
        "midi_file": midi_path,
    }

# Initialize the StateGraph
workflow = StateGraph(MusicState)

# Add nodes to the graph
workflow.add_node("melody_generator", melody_generator)
workflow.add_node("harmony_creator", harmony_creator)
workflow.add_node("rhythm_analyzer", rhythm_analyzer)
workflow.add_node("style_adapter", style_adapter)
workflow.add_node("midi_converter", midi_converter)

# Set the entry point of the graph
workflow.set_entry_point("melody_generator")

# Add edges to connect the nodes
workflow.add_edge("melody_generator", "harmony_creator")
workflow.add_edge("harmony_creator", "rhythm_analyzer")
workflow.add_edge("rhythm_analyzer", "style_adapter")
workflow.add_edge("style_adapter", "midi_converter")
workflow.add_edge("midi_converter", END)

# Compile the graph
app = workflow.compile()


# Define input parameters
inputs = {
        "musician_input": """
        Craft soothing and immersive Lofi music that effortlessly calms the mind, uplifts the soul, and creates a tranquil atmosphere perfect for relaxation, focus, and introspection. Blend soft melodies, gentle beats, and ambient textures to produce a seamless auditory escape that eases stress and enhances creativity. Infuse warmth and nostalgia into every note, allowing listeners to unwind, study, or drift into peaceful contemplation. Let the rhythm flow naturally, embracing imperfections that add character and authenticity. Whether for late-night musings or serene morning moments, shape a soundscape that resonates deeply, providing comfort, inspiration, and an enduring sense of inner peace.

        To achieve this, select instruments that evoke a sense of calm and nostalgia. Utilize warm piano chords, subtle guitar plucks, and mellow synth pads to establish a dreamy soundscape. The interplay between organic and electronic elements can enhance the emotional depth of the music. Soft vinyl crackles, nature sounds, and distant echoes further enrich the auditory experience, adding layers of texture that create a cozy and immersive ambiance.

        Percussion should be minimal yet effective. A steady but relaxed drum pattern with soft snares, brushed hi-hats, and deep yet unobtrusive kicks provides the foundation for the track. The groove should feel loose and natural, allowing room for melodies to breathe. Swing and slight timing imperfections give the music an organic quality that feels personal and handcrafted. Incorporating sampled drum breaks or designing beats with a vintage touch can amplify the nostalgic character of the piece.
            """,
            
        "style": "Lofi "
}

# Invoke the workflow
result = app.invoke(inputs)

print("Composition created")
print(f"MIDI file saved at: {result['midi_file']}")


def play_audio(file_path):
    """Play the generated audio file."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.quit()


print("To create and play a melody, run the following in a new cell:")
print("play_audio(result['midi_file'])")

play_audio(result["midi_file"])