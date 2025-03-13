from neomodel import (
    StructuredNode,
    StringProperty,
    ArrayProperty,
    BooleanProperty,
    RelationshipFrom,
    RelationshipTo,
    JSONProperty
)


class BasicMetadata(StructuredNode):
    """Basic Metadata Node"""
    news_type = StringProperty(required=True)
    who = ArrayProperty(StringProperty())
    when = ArrayProperty(StringProperty())
    where = ArrayProperty(StringProperty())
    what = ArrayProperty(StringProperty())
    why = ArrayProperty(StringProperty())
    how = ArrayProperty(StringProperty())
    has_basic_metadata = RelationshipTo("NewsText", "HAS_BASIC_METADATA")


class Knowledge(StructuredNode):
    """Knowledge Node"""
    term = StringProperty(required=True)
    category = StringProperty(required=True)
    description = StringProperty()
    source = StringProperty()


class NewsText(StructuredNode):
    """News Text Node"""
    content = StringProperty(required=True)
    # relationships
    has_basic_metadata = RelationshipFrom("BasicMetadata", "HAS_BASIC_METADATA")
    has_knowledge = RelationshipFrom("Knowledge", "HAS_KNOWLEDGE")
    has_check_point = RelationshipFrom("CheckPoint", "CHECKED_BY")


class CheckPoint(StructuredNode):
    """CheckPoint Node 和 CheckPoint State 相比，不继承 retrieval step"""
    content = StringProperty(required=True)
    is_verification_point = BooleanProperty(required=True)
    importance = StringProperty()
    # relationship
    verified_by = RelationshipFrom("RetrievalStep", "VERIFIED_BY")
        

class RetrievalStep(StructuredNode):
    """RetrievalStep Node"""
    purpose = StringProperty(required=True)
    expected_sources = ArrayProperty(StringProperty(), required=True)
    # relationship
    has_result = RelationshipFrom("SearchResult", "HAS_RESULT")
    supports_by = RelationshipFrom("Evidence", "SUPPORTS_BY")
    contradicts_with = RelationshipFrom("Evidence", "CONTRADICTS_WITH")


class SearchResult(StructuredNode):
    """SearchResult Node"""
    summary = StringProperty(required=True)
    conclusion = StringProperty(required=True)
    confidence = StringProperty(required=True)


class Evidence(StructuredNode):
    """Evidence node"""
    content = StringProperty(required=True)
    source = JSONProperty(required=True)
    relationship = StringProperty(required=True)
    reasoning = StringProperty(required=True)
