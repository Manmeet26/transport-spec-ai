# main.py

from query import ask_question

print("\nTransportation Spec AI")
print("Type 'exit' to quit\n")

while True:

    question = input(
        "Question: "
    )

    if question.lower() == "exit":
        break

    result = ask_question(
        question
    )

    print("\n")