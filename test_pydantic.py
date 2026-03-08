from pydantic import BaseModel
from pydantic_ai import Agent

class Item(BaseModel):
    a: str
    
agent = Agent('test', output_type=Item)
res = agent.run_sync('test')
print(getattr(res, 'data', None))
print(getattr(res, 'output', None))
