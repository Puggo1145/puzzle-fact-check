from neomodel import (
    StructuredNode,
    StringProperty,
    ArrayProperty,
    BooleanProperty,
    RelationshipFrom,
    JSONProperty
)


class NewsText(StructuredNode):
    """News Text Node"""
    content = StringProperty(required=True)
    # relationships
    basic_metadata = RelationshipFrom("BasicMetadata", "HAS_BASIC_METADATA")
    knowledge = RelationshipFrom("Knowledge", "HAS_KNOWLEDGE")
    check_point = RelationshipFrom("CheckPoint", "CHECKED_BY")


class BasicMetadata(StructuredNode):
    """Basic Metadata Node"""
    news_type = StringProperty(required=True)
    who = ArrayProperty(StringProperty())
    when = ArrayProperty(StringProperty())
    where = ArrayProperty(StringProperty())
    what = ArrayProperty(StringProperty())
    why = ArrayProperty(StringProperty())
    how = ArrayProperty(StringProperty())


class Knowledge(StructuredNode):
    """Knowledge Node"""
    term = StringProperty(required=True)
    category = StringProperty(required=True)
    description = StringProperty()
    source = StringProperty()


class CheckPoint(StructuredNode):
    """CheckPoint Node 和 CheckPoint State 相比，不继承 retrieval step"""
    content = StringProperty(required=True)
    is_verification_point = BooleanProperty(required=True)
    importance = StringProperty()
    # relationship
    retrieval_step = RelationshipFrom("RetrievalStep", "VERIFIED_BY")
        

class RetrievalStep(StructuredNode):
    """RetrievalStep Node"""
    purpose = StringProperty(required=True)
    expected_sources = ArrayProperty(StringProperty(), required=True)
    # relationship
    search_result = RelationshipFrom("SearchResult", "HAS_RESULT")


class SearchResult(StructuredNode):
    """SearchResult Node"""
    summary = StringProperty(required=True)
    conclusion = StringProperty(required=True)
    confidence = StringProperty(required=True)
    sources = ArrayProperty(StringProperty(), required=True)
    # relationships
    evidence_support = RelationshipFrom("Evidence", "SUPPORTS_BY")
    evidence_contradict = RelationshipFrom("Evidence", "CONTRADICTS_WITH")


class Evidence(StructuredNode):
    """Evidence node"""
    content = StringProperty(required=True)
    source = JSONProperty(required=True)
    relationship = StringProperty(required=True)
    reasoning = StringProperty(required=True)
