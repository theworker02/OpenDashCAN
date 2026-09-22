"""OpenDashCAN command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from opendashcan import __version__
from opendashcan.analysis.correlation import find_candidate_signals, summarize_ids
from opendashcan.core.startup import ClusterStartupSequencer
from opendashcan.core.translator import Translator
from opendashcan.registry import VEHICLES, get_decoder, get_encoder
from opendashcan.replay.reader import read_capture
from opendashcan.replay.simulator import SCENARIOS, iter_scenario
from opendashcan.replay.writer import write_json


def cmd_info(_: argparse.Namespace) -> int:
    print(f"OpenDashCAN {__version__}")
    print("Product: OpenDashCAN Desktop - installable Python program (CLI + Qt)")
    print("         NOT a website; NOT an ECU flash tool; NOT auto TX")
    print("Primary: PC-side OBD/CAN sniff -> decode -> VehicleState / gaps / IDs seen")
    print("Pipeline (research): Source CAN -> Decoder -> VehicleState ->")
    print("         ClusterEnvironment -> Target Encoder -> Donor Cluster (offline)")
    print("Install: pip install -e '.[gui,hw]'")
    print("GUI:     opendashcan-gui  or  opendashcan gui")
    print("Listen:  opendashcan listen --virtual   # or --interface socketcan ...")
    print("Phase: Phase 4 Cluster Protocol Reconstruction")
    print("ID style: dotted (honda.civic.gen10.us) - legacy aliases still resolve")
    print("Safety:  LISTEN_ONLY / EncodeMode.NO_OUTPUT / LinkMode.LISTEN_ONLY")
    print("         TX disabled (future: OPENDASHCAN_ALLOW_TX + allowlist only)")
    return 0


def cmd_listen(args: argparse.Namespace) -> int:
    """Live or offline listen-only decode (no TX to vehicle or cluster)."""
    from opendashcan.hw.listen import (
        DEFAULT_BITRATE,
        DEFAULT_VEHICLE,
        HardwareUnavailableError,
        iter_bus_frames,
        iter_capture_frames,
        open_listen_bus,
        python_can_available,
        resolve_virtual_fixture,
    )
    from opendashcan.hw.session import ListenSession
    from opendashcan.hw.tx_guard import refuse_send_message

    vehicle = args.vehicle or DEFAULT_VEHICLE
    try:
        decoder = get_decoder(vehicle)
    except KeyError as exc:
        print(f"unknown / undocumented vehicle decoder: {exc}", file=sys.stderr)
        print(
            "Decode only registered layouts (e.g. honda.civic.gen10.us).",
            file=sys.stderr,
        )
        return 1

    print("=== LISTEN ONLY - NO TRANSMIT ===")
    print(refuse_send_message())
    print(f"vehicle={vehicle}  decoder={decoder.display_name}")

    frame_iter: object
    source_label: str

    if args.capture:
        path = Path(args.capture)
        if not path.is_file():
            print(f"capture not found: {path}", file=sys.stderr)
            return 1
        frame_iter = iter_capture_frames(path)
        source_label = f"offline capture {path}"
    elif args.virtual:
        try:
            path = resolve_virtual_fixture(args.fixture)
        except FileNotFoundError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        frame_iter = iter_capture_frames(path)
        source_label = f"virtual/synthetic replay {path}"
        print("Note: SYNTHETIC fixture - not real vehicle data.")
    else:
        if not python_can_available():
            print(
                "python-can not installed; cannot open a live interface.\n"
                '  pip install -e ".[hw]"\n'
                "Or degrade gracefully:\n"
                "  opendashcan listen --virtual\n"
                "  opendashcan listen --capture captures/synthetic/idle_scenario.log\n"
                "Get frames onto the PC: hardware/can_recorder_rpi/README.md",
                file=sys.stderr,
            )
            return 1
        bustype = args.interface
        channel = args.channel
        bitrate = int(args.bitrate) if args.bitrate else DEFAULT_BITRATE
        try:
            bus = open_listen_bus(bustype=bustype, channel=channel, bitrate=bitrate)
        except HardwareUnavailableError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        frame_iter = iter_bus_frames(bus, max_frames=args.max_frames)
        source_label = f"{bustype}:{channel} @ {bitrate} LISTEN_ONLY"

    print(f"source: {source_label}")
    session = ListenSession(decoder=decoder)
    print_every = max(1, int(args.print_every))
    try:
        for frame in frame_iter:
            session.ingest(frame)
            if args.raw:
                print(
                    f"{frame.timestamp:10.4f}  {frame.arbitration_id:#05x}  "
                    f"{frame.data.hex().upper()}"
                )
            if session.frame_count % print_every == 0 and not args.raw:
                _print_listen_snapshot(session)
            if args.max_frames and session.frame_count >= args.max_frames:
                break
    except KeyboardInterrupt:
        print("\n(stopped)")

    print("--- final ---")
    _print_listen_snapshot(session)
    print(f"frames={session.frame_count}  elapsed={session.elapsed_s():.1f}s")
    return 0


def _print_listen_snapshot(session: object) -> None:
    from opendashcan.hw.session import ListenSession

    assert isinstance(session, ListenSession)
    print(f"[frames={session.frame_count}] known={session.state.known_signals()}")
    for row in session.id_rate_rows()[:12]:
        rate = f"{row.rate_hz:.1f} Hz" if row.rate_hz is not None else "n/a"
        print(f"  {row.arbitration_id:#05x}  count={row.count}  ~{rate}")
    for name, val, conf, ts in session.signal_rows()[:16]:
        print(f"  {name}={val}  confidence={conf}  t={ts}")


def cmd_vehicles(_: argparse.Namespace) -> int:
    seen: set[str] = set()
    for vid, info in VEHICLES.items():
        if vid in seen:
            continue
        seen.add(vid)
        print(f"{vid}")
        print(f"  name:  {info.display_name}")
        print(f"  role:  {info.role}")
        print(f"  years: {info.years}")
        print(f"  notes: {info.notes}")
    try:
        from opendashcan.registry import get_registry

        reg = get_registry()
        print("")
        print("Protocol platforms:")
        for pkg in reg.list_platforms():
            print(f"  {pkg.platform_id}  roles={pkg.vehicle.roles}")
    except Exception as exc:  # noqa: BLE001
        print(f"(protocol registry unavailable: {exc})", file=sys.stderr)
    return 0


def cmd_clusters(_: argparse.Namespace) -> int:
    from opendashcan.registry import get_registry

    reg = get_registry()
    for cid, pkg in reg.list_clusters():
        c = pkg.cluster
        assert c is not None
        print(f"{cid}")
        print(f"  platform: {pkg.platform_id}")
        print(f"  display:  {c.display_type}")
        print(f"  years:    {c.years_start}-{c.years_end}")
        print(f"  status:   {c.compatibility_status}")
        print(f"  reqs:     {len(pkg.requirements)}")
    return 0


def cmd_signals(args: argparse.Namespace) -> int:
    if args.vehicle in VEHICLES:
        info = VEHICLES[args.vehicle]
        if info.role == "source":
            mapping = get_decoder(args.vehicle).supported_signals()
        else:
            mapping = get_encoder(args.vehicle).supported_signals()
        for name, conf in sorted(mapping.items()):
            print(f"{name}: {conf}")
        return 0
    from opendashcan.registry import get_registry

    try:
        pkg = get_registry().get(args.vehicle)
    except KeyError:
        print(f"unknown vehicle: {args.vehicle}", file=sys.stderr)
        return 1
    for sig in sorted(pkg.signals, key=lambda s: s.signal):
        print(f"{sig.signal}: {sig.confidence.value}")
    return 0


def _print_decoded_state(state: object) -> None:
    known = state.known_signals()  # type: ignore[attr-defined]
    print(f"known_signals={known}")
    for name in known:
        sig = state.get(name) if hasattr(state, "get") else getattr(state, name, None)
        if sig is None:
            continue
        val = getattr(sig, "value", sig)
        conf = getattr(sig, "confidence", None)
        conf_s = conf.value if conf is not None and hasattr(conf, "value") else conf
        print(f"  {name}={val!r} confidence={conf_s}")


def cmd_replay(args: argparse.Namespace) -> int:
    frames = list(read_capture(args.capture))
    print(f"read {len(frames)} frames from {args.capture}")
    for stats in summarize_ids(frames)[: args.limit]:
        period = f"{stats.mean_period_s:.4f}s" if stats.mean_period_s is not None else "n/a"
        print(
            f"  {stats.arbitration_id:#x}: count={stats.count} period~{period} "
            f"dlc={list(stats.dlc_set)}"
        )
    if args.decode:
        decoder = get_decoder(args.decode)
        state = decoder.decode_frames(frames)
        print(f"decoded with {args.decode}:")
        _print_decoded_state(state)
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    decoder = get_decoder(args.source)
    encoder = get_encoder(args.target)
    translator = Translator(
        decoder,
        encoder,
        sequencer=ClusterStartupSequencer(require_ignition=False),
        emit_while_inactive=True,
    )
    if args.scenario:
        all_out = []
        for step, state in iter_scenario(args.scenario):
            translator.state = state
            phase = translator.sequencer.observe_state(state)
            out = encoder.encode(state, timestamp=step.t)
            all_out.extend(out)
            print(
                f"t={step.t:.1f} {step.label}: phase={phase.value} "
                f"rpm={step.rpm} speed={step.speed_kph} out_frames={len(out)}"
            )
        if args.output:
            write_json(args.output, all_out, label=f"synthetic:{args.scenario}")
            print(f"wrote {args.output} (SYNTHETIC research frames; no cluster claim)")
        return 0

    frames = list(read_capture(args.capture))
    result = translator.process_frames(frames)
    print(f"processed {len(frames)} source frames")
    print(f"startup_phase={result.startup_phase.value}")
    print(f"output_frames={len(result.output_frames)}")
    print(f"known_signals={result.state.known_signals()}")
    if args.decode_only:
        _print_decoded_state(result.state)
    if args.output:
        write_json(args.output, result.output_frames, label="translate")
        print(f"wrote {args.output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[1]
    tool = root / "tools" / "validate_evidence.py"
    if not tool.exists():
        print("validate_evidence.py missing", file=sys.stderr)
        return 1
    import runpy

    sys.argv = ["validate_evidence.py", *([str(args.path)] if args.path else [])]
    try:
        runpy.run_path(str(tool), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    frames = list(read_capture(args.capture))
    cands = find_candidate_signals(frames, min_count=args.min_count)
    print(
        json.dumps(
            [
                {
                    "id": hex(c.arbitration_id),
                    "count": c.count,
                    "mean_period_s": c.mean_period_s,
                    "dlc": list(c.dlc_set),
                    "samples": list(c.data_hex_samples),
                }
                for c in cands
            ],
            indent=2,
        )
    )
    if args.decode:
        decoder = get_decoder(args.decode)
        state = decoder.decode_frames(frames)
        print(f"decoded with {args.decode}:")
        _print_decoded_state(state)
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    from opendashcan.adaptation.planner import plan

    source = args.source or args.vehicle
    cluster = args.cluster
    if not source or not cluster:
        print("plan requires source and cluster", file=sys.stderr)
        return 1
    try:
        adaptation = plan(source, cluster)
    except KeyError as exc:
        print(f"plan failed: {exc}", file=sys.stderr)
        return 1
    print(adaptation.format_text())
    return 0


def cmd_build_adapter(args: argparse.Namespace) -> int:
    from opendashcan.adaptation.compiler import build_adapter

    try:
        out = build_adapter(
            args.source,
            args.target,
            documentation_only=bool(args.documentation_only),
        )
    except KeyError as exc:
        print(f"build-adapter failed: {exc}", file=sys.stderr)
        return 1
    status_path = out / "status.json"
    status = "PARTIAL"
    if status_path.is_file():
        status = json.loads(status_path.read_text(encoding="utf-8")).get("status", status)
    print(f"wrote adapter to {out}")
    print(f"status: {status}")
    print("Label: SOFTWARE VALIDATION ONLY / DOCUMENTATION_ONLY")
    return 0


def cmd_coverage(args: argparse.Namespace) -> int:
    from opendashcan.adaptation.matrix import (
        generate_adaptations_md,
        generate_cluster_coverage_md,
        generate_honda_coverage_md,
        write_coverage_docs,
    )

    if args.write:
        written = write_coverage_docs()
        for _name, path in written.items():
            print(f"wrote {path}")
        return 0
    which = args.matrix or "honda"
    if which == "honda":
        print(generate_honda_coverage_md())
    elif which == "cluster":
        print(generate_cluster_coverage_md())
    else:
        print(generate_adaptations_md())
    return 0


def cmd_registry(args: argparse.Namespace) -> int:
    from opendashcan.registry import get_registry

    reg = get_registry()
    kind = args.kind
    target = getattr(args, "target", None)

    if kind == "vehicles":
        for pkg in reg.list_platforms():
            print(pkg.platform_id)
        return 0
    if kind == "clusters":
        for cid, pkg in reg.list_clusters():
            print(f"{cid}\t{pkg.platform_id}")
        return 0
    if kind == "signal":
        name = args.signal_name or target
        if not name:
            print("registry signal requires a signal path or --name", file=sys.stderr)
            return 1
        hits = list(reg.platforms_for_signal(name))
        if not hits:
            print(f"no implementations for {name}")
            return 0
        for pkg, enc in hits:
            print(f"{pkg.platform_id}\t{enc.signal}\t{enc.arbitration_id}\t{enc.confidence.value}")
        return 0

    packages = [reg.get(target)] if target else reg.list_platforms()
    if kind == "buses":
        for pkg in packages:
            for b in pkg.buses:
                print(f"{pkg.platform_id}\t{b.bus_id}\t{b.bitrate}\t{b.confidence.value}")
        return 0
    if kind == "modules":
        for pkg in packages:
            for mod in pkg.modules:
                print(f"{pkg.platform_id}\t{mod.module_id}\t{mod.confidence.value}")
        return 0
    if kind == "messages":
        for pkg in packages:
            for msg in pkg.messages:
                print(
                    f"{pkg.platform_id}\t{msg.arbitration_id}\t{msg.name}\t{msg.confidence.value}"
                )
        return 0
    if kind == "signals":
        for pkg in packages:
            for sig in pkg.signals:
                print(f"{pkg.platform_id}\t{sig.signal}\t{sig.confidence.value}")
        return 0
    print(f"unknown registry kind: {kind}", file=sys.stderr)
    return 1


def cmd_protocol_diff(args: argparse.Namespace) -> int:
    from opendashcan.analysis.protocol_diff import diff_platforms

    try:
        result = diff_platforms(args.source, args.target)
    except KeyError as exc:
        print(f"protocol-diff failed: {exc}", file=sys.stderr)
        return 1
    print(result.format_text())
    return 0


def cmd_dbc(args: argparse.Namespace) -> int:
    from opendashcan.dbc import (
        export_platform_catalog,
        import_dbc,
        taxonomy_implementations_from_imports,
        write_conflict_report,
        write_import_artifacts,
    )

    if args.dbc_command == "import":
        result = import_dbc(
            args.file,
            compare_platform=args.platform,
            vehicle=args.vehicle,
            source=args.source or "opendbc",
            bus=args.bus or "vehicle_can",
        )
        if args.output_dir:
            arts = write_import_artifacts(result, args.output_dir)
            print(f"wrote {arts['json']} ({len(result.messages)} messages)")
            print(f"wrote {arts['yaml']}")
        else:
            out = args.output or Path("dist") / "dbc_import.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")
            print(
                f"wrote {out} ({len(result.messages)} messages, "
                f"{sum(len(m.signals) for m in result.messages)} signals)"
            )
        if result.conflicts:
            report = Path("DBC_CONFLICT_REPORT.md")
            write_conflict_report(result, report)
            print(f"wrote {report} ({len(result.conflicts)} conflicts - REQUIRES REVIEW)")
        for note in result.notes:
            print(f"note: {note}")
        return 0
    if args.dbc_command == "export":
        catalog = export_platform_catalog(args.platform)
        safe = args.platform.replace(":", ".").replace("/", ".")
        out = args.output or Path("dist") / f"{safe}.catalog.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
        return 0
    if args.dbc_command == "index":
        index_dir = args.index_dir or Path("dbc/opendbc/index")
        cross = taxonomy_implementations_from_imports(index_dir)
        signal = args.signal
        if signal:
            rows = cross.get(signal, [])
            if not rows:
                print(
                    f"{signal}: not found in imported DBC indexes (may be absent from public DBC)"
                )
                return 1
            for row in rows:
                print(
                    f"{signal}\t{row.get('vehicle_id')}\t{row.get('arbitration_id')}\t"
                    f"{row.get('message')}\t{row.get('start_bit')}|{row.get('length')}\t"
                    f"knowledge={row.get('knowledge_level')}"
                )
            return 0
        for tax in sorted(cross):
            print(f"{tax}: {len(cross[tax])} implementation(s)")
        return 0
    print("dbc requires 'import', 'export', or 'index'", file=sys.stderr)
    return 1


def cmd_virtual_cluster(args: argparse.Namespace) -> int:
    from opendashcan.adaptation.gating import EncodeMode
    from opendashcan.adaptation.virtual_cluster import VirtualCluster, run_software_validation
    from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState
    from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder

    state = VehicleState()
    state.engine_rpm = SignalValue(
        float(args.rpm), confidence=Confidence.INFERRED, validity=Validity.VALID
    )
    state.vehicle_speed = SignalValue(
        float(args.speed), confidence=Confidence.INFERRED, validity=Validity.VALID
    )
    encoder = Civic10Encoder(encode_mode=EncodeMode.SYNTHETIC)
    frames = encoder.encode(state, timestamp=0.0)
    vc = VirtualCluster(cluster_id=args.cluster)
    summary = run_software_validation(vc, frames)
    print(json.dumps(summary, indent=2))
    print("Label: SOFTWARE VALIDATION ONLY - no hardware claim")
    return 0


def cmd_cluster(args: argparse.Namespace) -> int:
    from opendashcan.cluster.environment_loader import list_cluster_envs, load_cluster_env
    from opendashcan.cluster.gaps import build_gap_report, format_gaps_text

    sub = args.cluster_command
    if sub == "list":
        for key in list_cluster_envs():
            env = load_cluster_env(key)
            print(f"{key}\t{env.cluster_id}\t{env.platform_id}")
        return 0

    if not args.cluster_name:
        print(
            "cluster command requires a cluster name (civic10|civic11|accord10|crv5)",
            file=sys.stderr,
        )
        return 1
    try:
        env = load_cluster_env(args.cluster_name)
    except KeyError as exc:
        print(f"cluster failed: {exc}", file=sys.stderr)
        return 1

    if sub == "show":
        print(json.dumps(env.environment, indent=2))
        print(f"requirements: {len(env.requirement_rows())}")
        print(f"rx_messages: {len(env.rx_rows())}")
        return 0
    if sub == "gaps":
        report = build_gap_report(args.cluster_name)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(format_gaps_text(report))
        return 0
    if sub == "messages":
        for m in env.rx_rows():
            print(
                f"{m.get('arbitration_id')}\t{m.get('name')}\t"
                f"{m.get('cluster_rx_class')}\t{m.get('notes', '')}"
            )
        return 0
    if sub == "requirements":
        for r in env.requirement_rows():
            print(
                f"{r.get('signal')}\t{r.get('priority')}\t"
                f"{r.get('arbitration_id')}\t{r.get('cluster_rx_class')}"
            )
        return 0
    print(f"unknown cluster subcommand: {sub}", file=sys.stderr)
    return 1


def cmd_correlate(args: argparse.Namespace) -> int:
    from opendashcan.analysis.similarity import correlate_message_id, correlate_signal

    if args.signal:
        hits = correlate_signal(target=args.target, signal=args.signal)
        print(json.dumps([h.to_dict() for h in hits], indent=2))
        if not hits:
            print(
                f"no implementations for {args.signal} (may be absent from public DBC)",
                file=sys.stderr,
            )
            return 1
        return 0
    if args.id is not None:
        aid = int(args.id, 0) if isinstance(args.id, str) else int(args.id)
        print(json.dumps(correlate_message_id(target=args.target, arbitration_id=aid), indent=2))
        return 0
    print("correlate requires --signal or --id", file=sys.stderr)
    return 1


def cmd_lineage(args: argparse.Namespace) -> int:
    from opendashcan.analysis.lineage import build_lineage, write_lineage_artifacts

    data = build_lineage()
    if args.write:
        paths = write_lineage_artifacts(data)
        print(f"wrote {paths['json']}")
        print(f"wrote {paths['md']}")
    if args.id:
        aid = int(args.id, 0)
        for g in data["id_groups"]:
            if g["id_dec"] == aid:
                print(json.dumps(g, indent=2))
                return 0
        print(f"ID {hex(aid)} not found in lineage", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "message_instances": data["message_instances"],
                "unique_ids": data["unique_ids"],
                "stable_count": len(data["stable_ids_identical_encoding"]),
                "divergent_count": len(data["divergent_ids"]),
                "name_collisions": len(data["name_collisions"]),
                "warning": data["warning"],
            },
            indent=2,
        )
    )
    return 0


def cmd_conflicts(args: argparse.Namespace) -> int:
    from opendashcan.analysis.conflicts_engine import collect_conflicts, format_conflicts_text

    data = collect_conflicts()
    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(format_conflicts_text(data))
    return 0


def cmd_generate_trace(args: argparse.Namespace) -> int:
    from opendashcan.cluster.trace import write_trace

    try:
        paths = write_trace(
            args.cluster,
            args.scenario,
            output=args.output,
        )
    except KeyError as exc:
        print(f"generate-trace failed: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {paths['candump']}")
    print(f"wrote {paths['manifest']}")
    print("Label: SYNTHETIC / SOFTWARE VALIDATION ONLY — unknowns omitted")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    from opendashcan.analysis.correlation import diff_ids
    from opendashcan.analysis.diff import payload_changes

    a = list(read_capture(args.a))
    b = list(read_capture(args.b))
    d = diff_ids(a, b)
    print("IDs only in A:", [hex(x) for x in sorted(d.get("only_a", d.get("a_only", set())))])
    print("IDs only in B:", [hex(x) for x in sorted(d.get("only_b", d.get("b_only", set())))])
    both = d.get("both", d.get("shared", set()))
    print("IDs in both:", [hex(x) for x in sorted(both)])
    changes = payload_changes(a, b)
    print(f"payload changes (first occurrence): {len(changes)}")
    for c in changes[: args.limit]:
        print(f"  {c['id']}: {c['a']} -> {c['b']}")
    return 0


def cmd_gui(args: argparse.Namespace) -> int:
    """Launch the Qt desktop GUI (optional ``.[gui]`` extra)."""
    from opendashcan.gui.app import main as gui_main

    argv: list[str] = []
    if getattr(args, "offscreen", False):
        argv.append("--offscreen")
    return gui_main(argv)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="opendashcan",
        description=(
            "OpenDashCAN Desktop - PC-side OBD/CAN listen + decode research tool "
            "(CLI + Qt; not a website; not an ECU flash tool; listen-only by default)"
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("info", help="Project info")
    sp.set_defaults(func=cmd_info)

    sp = sub.add_parser(
        "listen",
        help="LISTEN_ONLY live/offline CAN sniff + decode (no TX)",
    )
    sp.add_argument(
        "--vehicle",
        default="honda.civic.gen10.us",
        help="Registered decoder id (default honda.civic.gen10.us)",
    )
    sp.add_argument(
        "--interface",
        default="socketcan",
        choices=["socketcan", "pcan", "slcan", "virtual"],
        help="python-can bustype (ignored with --virtual / --capture)",
    )
    sp.add_argument("--channel", default="can0", help="Channel (can0, PCAN_USBBUS1, COM3, ...)")
    sp.add_argument("--bitrate", type=int, default=500_000, help="Bitrate (default 500000)")
    sp.add_argument(
        "--virtual",
        action="store_true",
        help="No hardware: replay synthetic fixture (graceful degrade)",
    )
    sp.add_argument(
        "--fixture",
        type=Path,
        help="Override synthetic fixture path used by --virtual",
    )
    sp.add_argument(
        "--capture",
        type=Path,
        help="Offline ASC/candump file (same decode view as live)",
    )
    sp.add_argument("--max-frames", type=int, default=None, help="Stop after N frames")
    sp.add_argument(
        "--print-every",
        type=int,
        default=25,
        help="Print ID/signal snapshot every N frames (non-raw)",
    )
    sp.add_argument("--raw", action="store_true", help="Print every frame hex line")
    sp.set_defaults(func=cmd_listen)

    sp = sub.add_parser("vehicles", help="List supported vehicles/platforms")
    sp.set_defaults(func=cmd_vehicles)

    sp = sub.add_parser("clusters", help="List target donor clusters")
    sp.set_defaults(func=cmd_clusters)

    sp = sub.add_parser("signals", help="List documented signals + confidence")
    sp.add_argument("vehicle", help="Vehicle / cluster / platform id")
    sp.set_defaults(func=cmd_signals)

    sp = sub.add_parser("replay", help="Summarize an offline capture")
    sp.add_argument("capture", type=Path)
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument(
        "--decode",
        metavar="VEHICLE",
        help="Also decode frames with a registered decoder (e.g. honda.civic.gen10.us)",
    )
    sp.set_defaults(func=cmd_replay)

    sp = sub.add_parser("translate", help="Offline translate (no physical TX)")
    sp.add_argument("--source", default="honda_civic_8th_gen")
    sp.add_argument("--target", default="honda_civic_10th_gen")
    sp.add_argument("--capture", type=Path, help="Source capture path")
    sp.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        help="Synthetic VehicleState scenario (not a cluster compatibility demo)",
    )
    sp.add_argument(
        "--decode-only",
        action="store_true",
        help="Print decoded VehicleState details (still runs encoder unless NO_OUTPUT)",
    )
    sp.add_argument("--output", type=Path)
    sp.set_defaults(func=cmd_translate)

    sp = sub.add_parser("validate", help="Validate evidence YAML files")
    sp.add_argument("path", nargs="?", type=Path)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("analyze", help="Heuristic signal discovery on a capture")
    sp.add_argument("capture", type=Path)
    sp.add_argument("--min-count", type=int, default=5)
    sp.add_argument(
        "--decode",
        metavar="VEHICLE",
        help="Also decode frames with a registered decoder (e.g. honda.civic.gen10.us)",
    )
    sp.set_defaults(func=cmd_analyze)

    sp = sub.add_parser("plan", help="Adaptation plan (documentation-only)")
    sp.add_argument("source", nargs="?", help="Source vehicle id")
    sp.add_argument("cluster", nargs="?", help="Target cluster id")
    sp.add_argument("--vehicle", help="Alias for source (legacy)")
    sp.add_argument("--cluster", dest="cluster_opt", help="Alias for cluster (legacy)")
    sp.set_defaults(func=cmd_plan)

    sp = sub.add_parser("build-adapter", help="Compile adaptation spec to dist/adapters/")
    sp.add_argument("source", help="Source vehicle id")
    sp.add_argument("target", help="Target cluster id")
    sp.add_argument(
        "--documentation-only",
        action="store_true",
        default=True,
        help="Documentation-only build (default)",
    )
    sp.set_defaults(func=cmd_build_adapter)

    sp = sub.add_parser("coverage", help="Print or write coverage matrices")
    sp.add_argument(
        "--matrix",
        choices=["honda", "cluster", "adaptations"],
        default="honda",
    )
    sp.add_argument("--write", action="store_true", help="Write docs/generated/*.md")
    sp.set_defaults(func=cmd_coverage)

    sp = sub.add_parser("registry", help="Query protocol registry")
    sp.add_argument(
        "kind",
        choices=["vehicles", "buses", "modules", "messages", "signals", "clusters", "signal"],
    )
    sp.add_argument(
        "target",
        nargs="?",
        help="Platform id (for buses/messages/…) or signal path (for signal)",
    )
    sp.add_argument("--name", dest="signal_name", help="Signal path for 'signal' kind")
    sp.set_defaults(func=cmd_registry)

    sp = sub.add_parser("virtual-cluster", help="SOFTWARE VALIDATION ONLY virtual cluster")
    sp.add_argument("--cluster", default="honda.civic.gen10.cluster.digital")
    sp.add_argument("--rpm", type=float, default=1500.0)
    sp.add_argument("--speed", type=float, default=40.0)
    sp.set_defaults(func=cmd_virtual_cluster)

    sp = sub.add_parser("diff", help="Diff two offline captures by ID/payload")
    sp.add_argument("a", type=Path)
    sp.add_argument("b", type=Path)
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_diff)

    sp = sub.add_parser("protocol-diff", help="Diff two protocol platforms")
    sp.add_argument("source", help="Source platform id")
    sp.add_argument("target", help="Target platform id")
    sp.set_defaults(func=cmd_protocol_diff)

    sp = sub.add_parser(
        "gui",
        help="Launch Qt desktop GUI (requires: pip install -e '.[gui]')",
    )
    sp.add_argument(
        "--offscreen",
        action="store_true",
        help="Qt offscreen platform (smoke / CI)",
    )
    sp.set_defaults(func=cmd_gui)

    sp = sub.add_parser("dbc", help="DBC import/export with conflict detection")
    dbc_sub = sp.add_subparsers(dest="dbc_command", required=True)
    imp = dbc_sub.add_parser(
        "import",
        help="Import DBC with full signal provenance (no auto CLUSTER_RX promotion)",
    )
    imp.add_argument("file", type=Path)
    imp.add_argument("--platform", help="Compare against registry platform")
    imp.add_argument("--vehicle", help="Vehicle / platform label for provenance")
    imp.add_argument("--source", default="opendbc", help="Source label (default opendbc)")
    imp.add_argument("--bus", default="vehicle_can", help="Bus label for provenance")
    imp.add_argument("-o", "--output", type=Path, help="Single JSON output path")
    imp.add_argument(
        "--output-dir",
        type=Path,
        help="Write JSON+YAML index pair into this directory",
    )
    imp.set_defaults(func=cmd_dbc)
    exp = dbc_sub.add_parser("export", help="Export registry catalog JSON (not a full DBC)")
    exp.add_argument("platform")
    exp.add_argument("-o", "--output", type=Path)
    exp.set_defaults(func=cmd_dbc)
    idx = dbc_sub.add_parser(
        "index",
        help="Query cross-vehicle taxonomy implementations from imported DBC indexes",
    )
    idx.add_argument("--signal", help="Taxonomy path e.g. powertrain.engine_rpm")
    idx.add_argument(
        "--index-dir",
        type=Path,
        default=Path("dbc/opendbc/index"),
        help="Directory of imported *.json indexes",
    )
    idx.set_defaults(func=cmd_dbc)

    # Phase 4 cluster environment / lineage / correlate / conflicts / traces
    sp = sub.add_parser("cluster", help="Query isolated cluster environments")
    csub = sp.add_subparsers(dest="cluster_command", required=True)
    for name, help_text in (
        ("list", "List cluster environment keys"),
        ("show", "Show environment.yaml summary"),
        ("gaps", "Eight-axis gap report"),
        ("messages", "RX message classification table"),
        ("requirements", "Display-function requirements"),
    ):
        cp = csub.add_parser(name, help=help_text)
        if name != "list":
            cp.add_argument(
                "cluster_name",
                help="civic10|civic11|accord10|crv5 or full cluster id",
            )
        else:
            cp.set_defaults(cluster_name=None)
        if name == "gaps":
            cp.add_argument("--json", action="store_true")
        cp.set_defaults(func=cmd_cluster)

    sp = sub.add_parser("correlate", help="Cross-platform signal/message similarity leads")
    sp.add_argument(
        "--target", required=True, help="Target vehicle id substring e.g. honda.civic.gen10"
    )
    sp.add_argument("--signal", help="Taxonomy signal e.g. powertrain.engine_rpm")
    sp.add_argument("--id", help="CAN ID (hex or int) for message-level correlate")
    sp.set_defaults(func=cmd_correlate)

    sp = sub.add_parser("lineage", help="Honda message lineage summary")
    sp.add_argument("--id", help="Focus on one CAN ID")
    sp.add_argument("--write", action="store_true", help="Write dist/ + research artifacts")
    sp.set_defaults(func=cmd_lineage)

    sp = sub.add_parser("conflicts", help="List preserved protocol/DBC conflicts")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_conflicts)

    sp = sub.add_parser(
        "generate-trace",
        help="Synthetic candump-compatible trace (omit unknowns; SOFTWARE ONLY)",
    )
    sp.add_argument("--cluster", required=True, help="civic10|civic11|accord10|crv5")
    sp.add_argument(
        "--scenario",
        required=True,
        choices=sorted(SCENARIOS),
        help="Synthetic VehicleState scenario",
    )
    sp.add_argument("-o", "--output", type=Path)
    sp.set_defaults(func=cmd_generate_trace)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "translate" and not args.scenario and not args.capture:
        parser.error("translate requires --capture or --scenario")
    if args.command == "plan":
        # Merge legacy --vehicle / --cluster flags
        if getattr(args, "cluster_opt", None) and not args.cluster:
            args.cluster = args.cluster_opt
        if args.vehicle and not args.source:
            args.source = args.vehicle
    code = args.func(args)
    raise SystemExit(code)


def main_listen(argv: list[str] | None = None) -> None:
    """Console-script entry for ``opendashcan-listen`` → ``listen`` subcommand."""
    rest = list(argv) if argv is not None else sys.argv[1:]
    main(["listen", *rest])


if __name__ == "__main__":
    main()
