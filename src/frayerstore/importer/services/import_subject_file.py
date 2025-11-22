from frayerstore.importer.yaml_utils import load_yaml


def import_subject_file(path, coordinator, report):
    data = load_yaml(path)
    coordinator.import_from_yaml(data, report)
