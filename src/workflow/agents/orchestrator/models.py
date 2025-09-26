from pydantic import BaseModel

class OrchestratorResponse(BaseModel):
    general_accounting: bool = False
    document_specific_data: bool = False
    data_visualization: bool = False