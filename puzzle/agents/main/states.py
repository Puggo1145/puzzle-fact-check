import uuid
import operator
from pydantic import BaseModel, Field
from ..metadata_extractor.states import MetadataState
from ..searcher.states import SearchResult, Evidence
from typing import Optional, List, Annotated, Literal

class IsNewsText(BaseModel):
    result: bool = Field(description="是否为可核查文本")
    reason: str = Field(description="判断依据")


class RetrievalResultVerification(BaseModel):
    reasoning: str = Field(
        description="对该检索步骤结论的推理",
    )
    verified: bool = Field(
        description="是否认可该检索步骤的结论",
        default=False
    )
    updated_purpose: Optional[str] = Field(
        description="如果对检索结果不满意，可以在此处更新该检索步骤的检索目的",
        default=None
    )
    updated_expected_source: Optional[str] = Field(
        description="如果对检索结果不满意，可以在此处更新该检索步骤的预期信息来源",
        default=None
    )


# 合并了 SearchResult 和 Evidence 的核查结论
class RetrievalResult(SearchResult):
    check_point_id: str
    retrieval_step_id: str
    evidences: Annotated[List[Evidence], operator.add] = Field(
        description="检索中收集的，与核查目标构成重要关系的证据片段",
        default_factory=list
    )


class RetrievalStep(BaseModel):
    id: str
    purpose: str = Field(
        description="该检索步骤的目的，想要获取什么信息",
    )
    expected_source: str = Field(description="期望信息的可能来源类型")
    result: Optional[RetrievalResult] = Field(
        description="search agent 检索后返回的核查结论",
        default=None
    )
    verification: Optional[RetrievalResultVerification] = Field(
        description="main agent 对 search agent 检索结果的复核",
        default=None
    )


class CheckPoint(BaseModel):
    id: str
    content: str = Field(description="从新闻中提取的事实陈述")
    is_verification_point: bool = Field(description="该陈述是否被选为核查点")
    importance: Optional[str] = Field(
        description="若被选为核查点，说明其重要性",
        default=None
    )
    retrieval_step: Optional[List[RetrievalStep]] = Field(
        description="若被选为核查点，提供检索方案", 
        default=None
    )

    
class CheckPoints(BaseModel):
    items: List[CheckPoint] = Field(description="从新闻文本中提取的核查点", default_factory=list)


class Result(BaseModel):
    report: str = Field(description="核查报告", default="")
    verdict: Literal[
        "true", # 真实 
        "mostly-true", # 大部分真实
        "mostly-false", # 大部分虚假
        "false", # 虚假
        "no-enough-evidence", # 无法证实
    ] = Field(
        description="核查结论评级",
        json_schema_extra={
            "true": "真实 - 陈述准确无误，没有任何重大遗漏",
            "mostly-true": "大部分真实 - 该陈述是准确的，但需要澄清或补充信息",
            "mostly-false": "大部分虚假 - 该陈述包含真实的成分，但忽略了可能会给人以不同印象的关键事实",
            "false": "虚假 - 该陈述不准确",
            "no-enough-evidence": "无法证实 - 没有足够证据支持该陈述，无法证实",
        }
    )


class FactCheckPlanState(BaseModel):
    news_text: str = Field(description="待核查的新闻文本")
    is_news_text: Optional[IsNewsText] = Field(description="是否为可核查文本", default=None)
    metadata: Optional[MetadataState] = Field(description="新闻元数据", default=None)
    check_points: List[CheckPoint] = Field(default_factory=list)
    result: Optional[Result] = Field(description="核查结果", default=None)
    
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
