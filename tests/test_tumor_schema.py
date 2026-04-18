from databases.experiment_database import ExperimentDatabase


def test_tumor_schema_creates_tumors_for_animal():
    db = ExperimentDatabase(":memory:")
    db.setup_experiment(
        name="Test",
        species="Mouse",
        uses_rfid=0,
        num_animals=2,
        num_groups=1,
        cage_max=2,
        measurement_type=1,
        experiment_id="exp",
        investigators=["A"],
        measurement="Tumor",
        calc_method=0,
        tumors_per_animal=2,
        tumor_labels=["Left", "Right"],
        measurement_mode="tumor",
    )
    db.setup_groups(["Control"], 2)
    db.add_animal(1, "1", 1, "")
    tumors = db.get_tumors_for_animal(1)
    assert len(tumors) == 2


def test_tumor_measurement_upsert_and_status():
    db = ExperimentDatabase(":memory:")
    db.setup_experiment(
        name="Test",
        species="Mouse",
        uses_rfid=0,
        num_animals=1,
        num_groups=1,
        cage_max=1,
        measurement_type=1,
        experiment_id="exp",
        investigators=["A"],
        measurement="Tumor",
        calc_method=0,
        tumors_per_animal=1,
        tumor_labels=["Left"],
        measurement_mode="tumor",
    )
    db.setup_groups(["Control"], 1)
    db.add_animal(1, "1", 1, "")
    tumor = db.get_tumors_for_animal(1)[0]
    tumor_id = tumor[0]
    db.upsert_tumor_measurement(tumor_id, "2026-01-01", 1.2, 0.8, "measured")
    first = db.get_tumor_measurement(tumor_id, "2026-01-01")
    assert first[0] == 1.2
    db.upsert_tumor_measurement(tumor_id, "2026-01-01", 2.0, 1.0, "invalid")
    second = db.get_tumor_measurement(tumor_id, "2026-01-01")
    assert second[0] == 2.0
