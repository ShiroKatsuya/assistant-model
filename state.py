# state.py

class State:
    def __init__(self, initial_data=None):
        """Initialize the state with optional initial data."""
        self.data = initial_data or {}
        # Initialize with the required keys for the graph
        self.keys = ["messages", "recall_memories"]  # Required keys
        
        # Initialize required keys with default values if not present
        for key in self.keys:
            if key not in self.data:
                self.data[key] = []

    def get(self, key, default=None):
        """Retrieve a value from the state."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Set a value in the state."""
        if key not in self.keys:
            self.keys.append(key)
        self.data[key] = value

    def update(self, updates):
        """Update the state with a dictionary of values."""
        for key in updates:
            if key not in self.keys:
                self.keys.append(key)
        self.data.update(updates)

    def __repr__(self):
        """Return a string representation of the state."""
        return f"State({self.data})"
        
    def __getitem__(self, key):
        """Allow dictionary-style access to state data."""
        return self.data[key]
        
    def __setitem__(self, key, value):
        """Allow dictionary-style setting of state data."""
        if key not in self.keys:
            self.keys.append(key)
        self.data[key] = value
        
    def to_dict(self):
        """Convert state to a dictionary."""
        return self.data

    def get_valid_keys(self):
        """Get list of valid keys that can be written to."""
        return self.keys

    @property
    def require_at_least_one_of(self):
        """Return list of keys that require at least one value."""
        # Return an empty list since we want to allow updates without any specific required keys
        return []