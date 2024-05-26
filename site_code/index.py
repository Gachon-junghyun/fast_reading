import openai

text = ""


# GPT-3.5 모델에 요청 보내기
response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "사용자에게 내용을 받으면 띄어쓰기를 고치고 문장단위로 줄바꿈을 해서 다시 줘\n 그리고 이게 논문 의 글자를 다 따온건데 출처 팩스 번호 출처등 내용과 관련없는 내용은 지우고 문맥에 맞는 내용만 남겨줘"},
        {"role": "user", "content": text}
    ]
)

# 응답 출력
print(response['choices'][0]['message']['content'])
