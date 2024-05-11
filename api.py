import os
import uvicorn
from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

abspath = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained("checkpoints/stable-code-instruct-3b", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("checkpoints/stable-code-instruct-3b", torch_dtype=torch.bfloat16,
                                             trust_remote_code=True)
model.eval()
model = model.cuda()


@app.post('/stable_code_instruct_3b')
def stable_code_instruct_3b(request_data: dict = Body(...)):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and polite code assistant",
        },
        {
            "role": "user",
            "content": f"{request_data['prompt']}"
        },
    ]

    prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)

    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)

    # 判断输入长度是否超过模型的最大长度
    if inputs.input_ids.shape[-1] > 4096:
        return JSONResponse(content="Input exceeds maximum length(4096)", status_code=413)

    tokens = model.generate(
        **inputs,
        max_new_tokens=16384,
        temperature=0.5,
        top_p=0.95,
        top_k=100,
        do_sample=True,
        use_cache=True
    )

    output = tokenizer.batch_decode(tokens[:, inputs.input_ids.shape[-1]:], skip_special_tokens=False)[0]
    return JSONResponse(content=output, status_code=200)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8181)
