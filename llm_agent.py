from langchain.agents import Tool
def generate_email_body(damage_info: str) -> str:
    # LLM call to format email
    from langchain import OpenAI, PromptTemplate, LLMChain
    template = PromptTemplate(
        input_variables=['info'],
        template="""
        Compose a concise incident report email based on:
        {info}
        """
    )
    chain = LLMChain(llm=OpenAI(temperature=0), prompt=template)
    return chain.run(info=damage_info)

class EmailTool(Tool):
    def __init__(self):
        super().__init__(
            name='GenerateEmail',
            func=lambda info: generate_email_body(info),
            description='Generate an email body from damage information.'
        )