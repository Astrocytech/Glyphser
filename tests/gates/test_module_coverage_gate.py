from __future__ import annotations

from pathlib import Path

from tooling.quality_gates import module_coverage_gate


def test_module_coverage_gate_passes_for_synthetic_xml(tmp_path: Path):
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        """<?xml version='1.0' ?>
<coverage>
  <packages>
    <package name="glyphser">
      <classes>
        <class filename="glyphser/public/verify.py" name="verify">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
          </lines>
        </class>
        <class filename="tooling/release/verify_release.py" name="verify_release">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
          </lines>
        </class>
        <class filename="tooling/quality_gates/spec_impl_congruence_gate.py" name="gate">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
""",
        encoding="utf-8",
    )

    report = module_coverage_gate.evaluate(xml)
    assert report["status"] == "PASS"
