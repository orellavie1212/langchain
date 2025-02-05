from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import BaseLLM
from langchain.llms.openai import BaseOpenAI
from langchain.pydantic_v1 import Field, root_validator
from langchain.schema.output import Generation, LLMResult


class VLLM(BaseLLM):
    """VLLM language model."""

    model: str = ""
    """The name or path of a HuggingFace Transformers model."""

    tensor_parallel_size: Optional[int] = 1
    """The number of GPUs to use for distributed execution with tensor parallelism."""

    trust_remote_code: Optional[bool] = False
    """Trust remote code (e.g., from HuggingFace) when downloading the model 
    and tokenizer."""

    n: int = 1
    """Number of output sequences to return for the given prompt."""

    best_of: Optional[int] = None
    """Number of output sequences that are generated from the prompt."""

    presence_penalty: float = 0.0
    """Float that penalizes new tokens based on whether they appear in the 
    generated text so far"""

    frequency_penalty: float = 0.0
    """Float that penalizes new tokens based on their frequency in the 
    generated text so far"""

    temperature: float = 1.0
    """Float that controls the randomness of the sampling."""

    top_p: float = 1.0
    """Float that controls the cumulative probability of the top tokens to consider."""

    top_k: int = -1
    """Integer that controls the number of top tokens to consider."""

    use_beam_search: bool = False
    """Whether to use beam search instead of sampling."""

    stop: Optional[List[str]] = None
    """List of strings that stop the generation when they are generated."""

    ignore_eos: bool = False
    """Whether to ignore the EOS token and continue generating tokens after 
    the EOS token is generated."""

    max_new_tokens: int = 512
    """Maximum number of tokens to generate per output sequence."""

    logprobs: Optional[int] = None
    """Number of log probabilities to return per output token."""

    dtype: str = "auto"
    """The data type for the model weights and activations."""

    download_dir: Optional[str] = None
    """Directory to download and load the weights. (Default to the default 
    cache dir of huggingface)"""

    vllm_obj: Optional[Any] = None
    """Holds `vllm.LLM` explicitly specified."""

    vllm_sampling_params_obj: Optional[Any] = None
    """Holds model sampling parameters valid for `vllm.LLM` call explicitly specified."""

    vllm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `vllm.LLM` call not explicitly specified."""

    client: Any  #: :meta private:

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that python package exists in environment."""

        try:
            from vllm import LLM as VLLModel
        except ImportError:
            raise ImportError(
                "Could not import vllm python package. "
                "Please install it with `pip install vllm`."
            )
        if not values["vllm_obj"]:
            values["client"] = VLLModel(
                model=values["model"],
                tensor_parallel_size=values["tensor_parallel_size"],
                trust_remote_code=values["trust_remote_code"],
                dtype=values["dtype"],
                download_dir=values["download_dir"],
                **values["vllm_kwargs"],
            )
        else:
            values["client"] = values["vllm_obj"]

        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling vllm."""
        return {
            "n": self.n,
            "best_of": self.best_of,
            "max_tokens": self.max_new_tokens,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "stop": self.stop,
            "ignore_eos": self.ignore_eos,
            "use_beam_search": self.use_beam_search,
            "logprobs": self.logprobs,
        }

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""

        if not self.vllm_sampling_params_obj:
            from vllm import SamplingParams
            # build sampling parameters
            params = {**self._default_params, **kwargs, "stop": stop}
            sampling_params = SamplingParams(**params)
        else:
            sampling_params = self.vllm_sampling_params_obj
        # call the model
        outputs = self.client.generate(prompts, sampling_params)

        generations = []
        for output in outputs:
            text = output.outputs[0].text
            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "vllm"


class VLLMOpenAI(BaseOpenAI):
    """vLLM OpenAI-compatible API client"""

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        openai_creds: Dict[str, Any] = {
            "api_key": self.openai_api_key,
            "api_base": self.openai_api_base,
        }

        return {
            "model": self.model_name,
            **openai_creds,
            **self._default_params,
            "logit_bias": None,
        }

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "vllm-openai"
