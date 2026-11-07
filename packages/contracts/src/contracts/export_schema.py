import json
from pathlib import Path

from pydantic.json_schema import models_json_schema

from contracts.models import (
    Agreement,
    Commitment,
    ConfirmRequest,
    ConfirmResponse,
    Driver,
    Entity,
    ErrorPayload,
    Language,
    Plan,
    PlanItem,
    TranslationResult,
    TripRequest,
    Utterance,
    WSEventEnvelope,
)

MODELS = [
    Language,
    Entity,
    Utterance,
    TranslationResult,
    ConfirmRequest,
    ConfirmResponse,
    Driver,
    TripRequest,
    PlanItem,
    Plan,
    Commitment,
    Agreement,
    ErrorPayload,
    WSEventEnvelope,
]


def export_schemas():
    root_dir = Path(__file__).resolve().parents[4]
    schemas_dir = root_dir / "packages" / "contracts" / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    # Use Pydantic multi-model schema generator to ensure
    # all shared $defs are in one unified schema
    model_tuples = [(m, "validation") for m in MODELS]
    _, top_level_schema = models_json_schema(
        model_tuples,
        title="VoicebridgeContracts",
        ref_template="#/$defs/{model}",
    )

    # Write combined schema
    contracts_file = schemas_dir / "contracts.json"
    with open(contracts_file, "w", encoding="utf-8") as f:
        json.dump(top_level_schema, f, indent=2)

    # Write individual model schemas with $defs included so each is self-contained
    defs = top_level_schema.get("$defs", {})
    for name, model_schema in defs.items():
        single_schema = dict(model_schema)
        single_schema["$defs"] = defs
        with open(schemas_dir / f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(single_schema, f, indent=2)

    print(f"Exported combined and individual JSON schemas to {schemas_dir}")


if __name__ == "__main__":
    export_schemas()
