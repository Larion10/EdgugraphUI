from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import abc
import ai71

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

class AI_API(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractclassmethod
    def messenge(self, promt:tuple[str, str], **kwargs) -> tuple[str, list[dict[str, str]]]:
        """kwargs: 
                history
                name
                parameters (temp, stb),
                """
        pass

    def create_input(self, promt:tuple[str, str], history:list[dict[str, str]]) -> list[dict[str, str]]:
        history.append({"role": "system", "content": promt[0]})
        history.append({"role": "user", "content": promt[1]}) #később alakítsd
        return(history)


    def create_output(self, output:str, history:list[dict[str, str]]) -> tuple[str, list[dict[str, str]]]:
        history.append({"role": "assistant", "content": output}) #később alakítsd
        return(output, history)


class AI_local(AI_API):
    def __init__(self) -> None:
        
        self.device = torch.device("mps")
        self.checkpoint = "HuggingFaceTB/SmolLM-1.7B-Instruct"

        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint, device_map=self.device)
        # for multiple GPUs install accelerate and do `model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")`
        self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint, device_map=self.device)


    def  messenge(self, promt:tuple[str, str], **kwargs) -> tuple[str, str]:
        messages = self.create_input(promt, kwargs["histroy"] if "history" in kwargs.keys() else [])
        input_text= self.tokenizer.apply_chat_template(messages, tokenize=False)
        inputs = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)
        outputs = self.model.generate(inputs, max_new_tokens=300, temperature=0.6, top_p=0.92, do_sample=True).to(self.device)
        
        out = self.tokenizer.decode(outputs[0])
        print(out)

        return(self.create_output(out, messages))
    

class AI71_api(AI_API):
    def __init__(self) -> None:
        self.client = ai71.AI71("ai71-api-6d918339-00a5-4fe6-8422-027b0e6f6089")

    async def messenge(self, promt:str, **kwargs):
        print("fut")
        mes = self.create_input(promt, kwargs["history"] if "history" in kwargs.keys() else [])
        res = self.client.chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=mes,
            top_k=5000,
            temperature=0.1
        )
        resstr = res.choices[0].message.content
        return(self.create_output(res.choices[0].message.content, mes))
    




