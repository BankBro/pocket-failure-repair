from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "eval" / "eval_official_tools.py"
SPEC = spec_from_file_location("eval_official_tools", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
EVAL_OFFICIAL_TOOLS = module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL_OFFICIAL_TOOLS)


def test_parse_plip_xml_builds_residue_fingerprint(tmp_path: Path) -> None:
    xml_path = tmp_path / "report.xml"
    xml_path.write_text(
        """
        <report>
          <hydrophobic_interaction>
            <reschain>A</reschain><resnr>42</resnr><restype>LEU</restype>
          </hydrophobic_interaction>
          <hydrogen_bond>
            <reschain>B</reschain><resnr>7</resnr><restype>ASP</restype>
          </hydrogen_bond>
          <hydrogen_bond>
            <reschain>B</reschain><resnr>7</resnr><restype>ASP</restype>
          </hydrogen_bond>
        </report>
        """,
        encoding="utf-8",
    )

    parsed = EVAL_OFFICIAL_TOOLS.parse_plip_xml(xml_path)

    assert parsed["plip_interaction_count"] == 3
    assert parsed["plip_interaction_counts"] == {"hydrophobic_interaction": 1, "hydrogen_bond": 2}
    assert parsed["plip_interaction_fingerprint"] == [
        "hydrogen_bond|B|7|ASP",
        "hydrophobic_interaction|A|42|LEU",
    ]
    assert parsed["plip_interaction_fingerprint_count"] == 2


def test_interaction_similarity_reports_recovery_and_jaccard() -> None:
    reference = {"hydrogen_bond|A|1|SER", "hydrophobic_interaction|A|2|LEU"}
    candidate = {"hydrogen_bond|A|1|SER", "salt_bridge|B|3|LYS"}

    metrics = EVAL_OFFICIAL_TOOLS.interaction_similarity(reference, candidate)

    assert metrics == {"similarity": 1 / 3, "recovery": 0.5, "recovered_count": 1}
