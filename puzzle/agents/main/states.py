import uuid
import operator
from pydantic import BaseModel, Field
from ..metadata_extractor.states import MetadataState
from ..searcher.states import SearchResult, Evidence
from typing import Optional, List, Annotated, Literal

class IsNewsText(BaseModel):
    result: bool = Field(description="Whether the text is suitable for fact-checking")
    reason: str = Field(description="The reason for the judgment")


class RetrievalResultVerification(BaseModel):
    reasoning: str = Field(
        description="The reasoning for the retrieval step conclusion",
    )
    verified: bool = Field(
        description="Whether to accept the retrieval step conclusion",
        default=False
    )
    updated_purpose: Optional[str] = Field(
        description="If the retrieval result is not satisfactory, you can update the retrieval purpose of the retrieval step here",
        default=None
    )
    updated_expected_source: Optional[str] = Field(
        description="If the retrieval result is not satisfactory, you can update the expected information source of the retrieval step here",
        default=None
    )


# 合并了 SearchResult 和 Evidence 的核查结论
class RetrievalResult(SearchResult):
    check_point_id: str
    retrieval_step_id: str
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="Evidence fragments collected during retrieval, which are important to the fact-checking goal",
        default_factory=list
    )


class RetrievalStep(BaseModel):
    id: str
    purpose: str = Field(
        description="The purpose of the retrieval step, what information to retrieve",
    )
    expected_source: str = Field(description="The possible source type of the expected information")
    result: Optional[RetrievalResult] = Field(
        description="The fact-checking conclusion returned by the search agent after retrieval",
        default=None
    )
    verification: Optional[RetrievalResultVerification] = Field(
        description="The verification of the retrieval result by the main agent",
        default=None
    )


class CheckPoint(BaseModel):
    id: str
    content: str = Field(description="The fact statement extracted from the news")
    is_verification_point: bool = Field(description="Whether the statement is selected as a verification point")
    importance: Optional[str] = Field(
        description="If it is selected as a verification point, explain its importance",
        default=None
    )
    retrieval_step: Optional[List[RetrievalStep]] = Field(
        description="If it is selected as a verification point, provide a retrieval plan", 
        default=None
    )

    
class CheckPoints(BaseModel):
    items: List[CheckPoint] = Field(description="The check points extracted from the news text", default_factory=list)


class Result(BaseModel):
    report: str = Field(description="The fact-checking report", default="")
    verdict: Literal[
        "true", # 真实 
        "mostly-true", # 大部分真实
        "mostly-false", # 大部分虚假
        "false", # 虚假
        "no-enough-evidence", # 无法证实
    ] = Field(
        description="The fact-checking conclusion rating",
        json_schema_extra={
            "true": "True - The statement is accurate and complete, without any major omissions",
            "mostly-true": "Mostly True - The statement is accurate, but needs clarification or additional information",
            "mostly-false": "Mostly False - The statement contains true components, but ignores key facts that may give a different impression",
            "false": "False - The statement is inaccurate",
            "no-enough-evidence": "No Enough Evidence - There is not enough evidence to support the statement, cannot be verified",
        }
    )


class FactCheckPlanState(BaseModel):
    news_text: str = Field(description="The news text to be fact-checked")
    is_news_text: Optional[IsNewsText] = Field(description="Whether the text is suitable for fact-checking", default=None)
    metadata: Optional[MetadataState] = Field(description="The metadata of the news", default=None)
    check_points: List[CheckPoint] = Field(default_factory=list)
    result: Optional[Result] = Field(description="The fact-checking result", default=None)
    
    def get_formatted_check_points(self, check_points: CheckPoints) -> List[CheckPoint]:
        """
        在 LLM 给出 check points 后为每个 check point 和 retrieval step 生成唯一 id
        并只保留 is_verification_point 为 True 的核查点
        """
        formatted_check_points = []
        
        for check_point in check_points.items:
            if check_point.is_verification_point and check_point.retrieval_step:
                # 创建新的 retrieval_step 列表，为每个 step 生成新的 id
                new_retrieval_steps = []
                for retrieval_step in check_point.retrieval_step:
                    # 为每个 retrieval_step 生成新的 id
                    new_retrieval_step = retrieval_step.model_copy(
                        update={"id": str(uuid.uuid4())}
                    )
                    new_retrieval_steps.append(new_retrieval_step)
                
                # 为 check_point 生成新的 id 并更新 retrieval_step
                new_check_point = check_point.model_copy(
                    update={
                        "id": str(uuid.uuid4()),
                        "retrieval_step": new_retrieval_steps
                    }
                )
                
                formatted_check_points.append(new_check_point)
        
        return formatted_check_points
