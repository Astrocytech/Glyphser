# Glyphser Test Coverage Gaps

Status: Draft

This document enumerates current coverage gaps between the operator registry and the test suite.

## Summary
- Total operators in registry: 27
- Operators referenced in tests: 2
- Operators missing direct test references: 25

## Missing Operators (No Direct Test References)
- Glyphser.Model.Forward
- Glyphser.DifferentialPrivacy.Apply
- Glyphser.TMMU.PrepareMemory
- Glyphser.Backend.LoadDriver
- Glyphser.IO.SaveCheckpoint
- Glyphser.Checkpoint.Restore
- Glyphser.Error.Emit
- Glyphser.Tracking.RunCreate
- Glyphser.Tracking.RunStart
- Glyphser.Tracking.RunEnd
- Glyphser.Tracking.MetricLog
- Glyphser.Tracking.ArtifactPut
- Glyphser.Tracking.ArtifactGet
- Glyphser.Tracking.ArtifactList
- Glyphser.Tracking.ArtifactTombstone
- Glyphser.Registry.VersionCreate
- Glyphser.Registry.StageTransition
- Glyphser.Monitor.Register
- Glyphser.Monitor.Emit
- Glyphser.Monitor.DriftCompute
- Glyphser.Trace.ComputeTraceHash
- Glyphser.Trace.TraceMigrate
- Glyphser.Import.LegacyFramework
- Glyphser.Checkpoint.CheckpointMigrate
- Glyphser.Config.ManifestMigrate

## Immediate Actions
- Add a per-operator conformance vector placeholder for each missing operator.
- Add minimal deterministic tests for each missing operator stub (input schema validation + deterministic error output).
- Extend hello-core or create a second fixture set to exercise at least one operator from each major domain.
