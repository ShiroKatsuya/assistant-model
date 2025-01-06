from haystack.nodes.prompt.invocation_layer import PromptModelInvocationLayer
from llama_cpp import Llama

class LlamaCPPInvocationLayer(PromptModelInvocationLayer):
    def __init__(self, model_name_or_path: str, **kwargs):
        super().__init__(model_name_or_path)
        self.model = Llama(model_path=model_name_or_path, **kwargs)

    def invoke(self, *args, **kwargs):
        response = self.model.create_completion(*args, **kwargs)
        return response["choices"][0]["text"]