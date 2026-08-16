from schemas import CategoryUpdate, ProductUpdate


def test_explicit_null_description_is_kept() -> None:
    assert ProductUpdate.model_validate({"description": None}).changes() == {"description": None}


def test_explicit_null_elsewhere_means_unchanged() -> None:
    assert ProductUpdate.model_validate({"name": None, "price": None}).changes() == {}


def test_unset_fields_are_absent() -> None:
    assert ProductUpdate.model_validate({}).changes() == {}
    assert CategoryUpdate.model_validate({}).changes() == {}


def test_set_values_pass_through() -> None:
    assert ProductUpdate.model_validate({"name": "Tea", "price": 100}).changes() == {"name": "Tea", "price": 100}
