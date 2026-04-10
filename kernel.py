"""
Kernel — Boucle cognitive principale de Genesis.

Flux : generate_objective → decompose → think → act → assess → evolve/learn → loop
"""

import json
import subprocess
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import genome as genome_module
import objective as objective_module
import fitness as fitness_module
import actions as actions_module
import memory as memory_module
import evolver as evolver_module
import reflect as reflect_module
import audit


class Kernel:
    def __init__(self, initial_objective: str = None, max_cycles: int = None):
        self.initial_objective = initial_objective
        self.max_cycles = max_cycles  # None = infini
        self.cycle_id = 0

        # État courant
        self.genome = None
        self.objective = None
        self.sub_goals = []
        self.current_sub_goal = None
        self.completed_sub_goals = []

        # Phase développementale (spiral curriculum)
        self.current_phase = "orient"
        self.current_goal_level = 1
        self.completed_phases = []  # phases complétées dans le spiral courant

        # Suivi stagnation
        self.stagnant_cycles = 0
        self.cycle_history = []
        self.last_action_result = None
        self.next_focus = None

    SESSION_PATH = Path("brain/session_state.json")

    def boot(self):
        """Initialise le kernel : charge génome, restaure session si existante."""
        Path("/tmp/genesis_workspace").mkdir(parents=True, exist_ok=True)

        self.genome = genome_module.load()

        # Restaurer la session précédente si elle existe
        restored = self._restore_session()

        audit.log_event("kernel_boot", {
            "genome_generation": self.genome["generation"],
            "initial_objective": self.initial_objective,
            "session_restored": restored,
        })

        # Synchroniser phase depuis le genome si pas de session restaurée
        if not restored:
            self.current_phase = self.genome.get("current_phase", "orient")
            self.current_goal_level = self.genome.get("current_goal_level", 1)

        if restored:
            print(f"\nGenesis resuming... Generation {self.genome['generation']} | Cycle {self.cycle_id} | Phase {self.current_phase.upper()} | Level {self.current_goal_level} | Objective: {self.objective['goal'][:60]}...")
        else:
            print(f"\nGenesis booting fresh... Generation {self.genome['generation']} | Phase {self.current_phase.upper()} | Goal Level {self.current_goal_level}")

    def _save_session(self):
        """Persiste l'état cognitif courant après chaque cycle."""
        state = {
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "cycle_id": self.cycle_id,
            "genome_generation": self.genome["generation"],
            "objective": self.objective,
            "sub_goals": self.sub_goals,
            "current_sub_goal": self.current_sub_goal,
            "completed_sub_goals": self.completed_sub_goals,
            "stagnant_cycles": self.stagnant_cycles,
            "next_focus": self.next_focus,
            "last_action_result_excerpt": (self.last_action_result or "")[:300],
            # Phase développementale
            "current_phase": self.current_phase,
            "current_goal_level": self.current_goal_level,
            "completed_phases": self.completed_phases,
        }
        self.SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.SESSION_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    def _restore_session(self) -> bool:
        """
        Restaure la session précédente si elle existe et est active.
        Retourne True si restauration réussie.
        """
        if self.initial_objective:
            # Objectif fourni explicitement → ignorer la session sauvegardée
            return False

        if not self.SESSION_PATH.exists():
            return False

        try:
            state = json.loads(self.SESSION_PATH.read_text())
        except Exception:
            return False

        obj = state.get("objective")
        if not obj or obj.get("status") == "completed":
            return False

        self.cycle_id = state.get("cycle_id", 0)
        self.objective = obj
        self.sub_goals = state.get("sub_goals", [])
        self.current_sub_goal = state.get("current_sub_goal")
        self.completed_sub_goals = state.get("completed_sub_goals", [])
        self.stagnant_cycles = state.get("stagnant_cycles", 0)
        self.next_focus = state.get("next_focus")
        self.last_action_result = state.get("last_action_result_excerpt")
        self.current_phase = state.get("current_phase", "orient")
        self.current_goal_level = state.get("current_goal_level", 1)
        self.completed_phases = state.get("completed_phases", [])
        return True

    def run(self):
        """Boucle cognitive principale."""
        self.boot()

        while True:
            try:
                # 1. Objectif
                if self.objective is None or self.objective.get("status") == "completed":
                    self._acquire_objective()

                # 2. Décomposition (si pas encore fait ou sous-buts épuisés)
                if not self.current_sub_goal:
                    self._decompose_objective()

                # 3. Cycle cognitif
                self._run_cycle()

                # 4. Vérifier limite de cycles
                if self.max_cycles and self.cycle_id >= self.max_cycles:
                    print(f"\nMax cycles ({self.max_cycles}) reached. Stopping.")
                    break

                time.sleep(1)  # Respiration entre cycles

            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                break
            except Exception as e:
                # Les erreurs sont des cycles BLOCKED — jamais un crash
                self._handle_error_as_blocked_cycle(e)

    def _acquire_objective(self):
        """Génère ou adopte l'objectif initial, contraint à la phase courante."""
        memory_ctx = memory_module.get_context({})

        if self.initial_objective and self.objective is None:
            # Objectif fourni par l'utilisateur — on le structure
            self.objective = {
                "goal": self.initial_objective,
                "success_criteria": [],
                "rationale": "User-provided objective",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "genome_generation": self.genome["generation"],
                "phase": self.current_phase,
            }
        else:
            # Auto-génération contrainte à la phase courante
            print(f"\nGenerating autonomous objective for phase {self.current_phase.upper()}...")
            self.objective = objective_module.generate(
                self.genome, memory_ctx, current_phase=self.current_phase
            )

        self.completed_sub_goals = []
        audit.log_event("objective_acquired", {
            "goal": self.objective["goal"],
            "genome_generation": self.genome["generation"],
            "phase": self.current_phase,
            "goal_level": self.current_goal_level,
        })
        audit.print_header(self.objective, self.genome)

    def _decompose_objective(self):
        """Décompose l'objectif en sous-buts."""
        print("\nDecomposing objective into sub-goals...")
        decomposition = objective_module.decompose(
            self.objective, self.genome, self.completed_sub_goals
        )
        self.sub_goals = decomposition.get("sub_goals", [])
        next_id = decomposition.get("next_sub_goal")

        self.current_sub_goal = next_id
        audit.log_event("decomposition", {
            "sub_goals": [sg["description"] for sg in self.sub_goals],
            "next": next_id,
        })

        if self.sub_goals:
            sg = next((s for s in self.sub_goals if s["id"] == next_id), self.sub_goals[0])
            print(f"  → Next sub-goal: {sg.get('description', next_id)}")

    # MUT-G36-001: when_artifact_missing_run_write_cmd_immediately_do_not_self_modify
    def _ensure_artifacts(self) -> bool:
        """
        Check whether required objective artifacts exist.
        If the genome's action_preferences defines an all_in_one_write_cmd,
        run it immediately when any required artifact is absent.
        Returns True if write command was triggered, False otherwise.
        """
        prefs = self.genome.get("action_preferences", {})
        write_cmd = prefs.get("all_in_one_write_cmd", "")
        if not write_cmd:
            return False

        # Derive artifact paths from OBJ_combined_audit_cmd or fitness_criteria
        criteria = self.genome.get("fitness_criteria", [])
        missing = []
        for criterion in criteria:
            if "exists" in criterion and "brain/" in criterion:
                # Extract filename hint from criterion string
                parts = [w for w in criterion.split("_") if w.endswith(".json") or "json" in w]
                for part in parts:
                    candidate = Path("brain") / part.replace("brain/", "")
                    if not candidate.exists():
                        missing.append(str(candidate))

        if missing:
            print(f"  [MUT-G36-001] Artifact(s) missing: {missing} — running write_cmd immediately")
            try:
                proc = subprocess.run(
                    write_cmd, shell=True, capture_output=True, text=True, timeout=60
                )
                print(f"  [write_cmd stdout] {proc.stdout.strip()[:200]}")
                if proc.returncode != 0:
                    print(f"  [write_cmd stderr] {proc.stderr.strip()[:200]}")
            except Exception as exc:
                print(f"  [write_cmd error] {exc}")
            return True
        return False

    # MUT-G36-002: run_combined_audit_command_verbatim_no_echo_substitution
    def _run_audit_verbatim(self) -> str:
        """
        Execute OBJ_combined_audit_cmd verbatim via subprocess.
        Never uses echo/printf substitution — opens actual files.
        Returns raw stdout from the audit command.
        """
        prefs = self.genome.get("action_preferences", {})
        audit_cmd = prefs.get("OBJ_combined_audit_cmd", "")
        if not audit_cmd:
            return ""
        try:
            proc = subprocess.run(
                audit_cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            output = proc.stdout.strip()
            print(f"  [MUT-G36-002] Audit output: {output[:300]}")
            return output
        except Exception as exc:
            print(f"  [audit_verbatim error] {exc}")
            return ""

    def _run_cycle(self):
        """Exécute un cycle complet : think → act → assess → evolve/learn."""
        self.cycle_id += 1

        # MUT-G36-001: ensure required artifacts exist before proceeding
        self._ensure_artifacts()

        # Contexte mémoire + réflexion
        memory_ctx = memory_module.get_context(self.objective)
        reflection_ctx = reflect_module.get_context(n=3)
        if reflection_ctx:
            memory_ctx = memory_ctx + "\n\n" + reflection_ctx if memory_ctx else reflection_ctx

        # Sub-goal courant (description)
        sg_obj = next(
            (s for s in self.sub_goals if s["id"] == self.current_sub_goal),
            {"id": self.current_sub_goal, "description": str(self.current_sub_goal)},
        )
        sg_description = sg_obj.get("description", str(self.current_sub_goal))

        # 3a. Proposer une action
        action = actions_module.propose(
            objective=self.objective,
            sub_goal=sg_description,
            genome=self.genome,
            memory_context=memory_ctx,
            last_result=self.last_action_result,
            next_focus=self.next_focus,
        )

        # 3a'. Si l'action elle-même est un dict d'erreur LLM → cycle BLOCKED
        if action.get("_llm_error"):
            return self._blocked_cycle(
                sg_description,
                f"LLM failed to propose action: {action.get('_error_msg', '?')}",
            )

        # 3b. Gérer self_modify comme signal (pas d'exécution directe)
        if action.get("type") == "self_modify":
            result = actions_module.execute(action, self.genome)
            fitness = {
                "status": "STAGNANT",
                "score": 0,
                "reason": "Self-modification requested — triggering evolution",
                "evidence": result,
                "next_focus": self.next_focus or "mutate and retry",
            }
            self.stagnant_cycles += 1
        else:
            # 3c. Exécuter l'action
            result = actions_module.execute(action, self.genome)

            # Gérer memory_query
            if result.startswith("MEMORY_QUERY:"):
                query = result.replace("MEMORY_QUERY:", "").strip()
                result = memory_module.query(query, self.genome)

            # 3d. Évaluer la fitness contre la phase courante
            fitness = fitness_module.assess(
                objective=self.objective,
                sub_goal=sg_description,
                action_taken=action,
                action_result=result,
                cycle_history=self.cycle_history,
                genome=self.genome,
                current_phase=self.current_phase,
            )
            # Si fitness est un dict d'erreur LLM → BLOCKED
            if fitness.get("_llm_error"):
                fitness = {
                    "status": "BLOCKED",
                    "score": 0,
                    "reason": f"LLM failed to assess fitness: {fitness.get('_error_msg', '?')}",
                    "evidence": result[:200],
                    "next_focus": "retry with simpler approach",
                }

        self.last_action_result = result
        self.next_focus = fitness.get("next_focus")

        # 4. Construire l'entrée de cycle
        cycle_entry = {
            "cycle_id": self.cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "genome_generation": self.genome["generation"],
            "phase": self.current_phase,
            "goal_level": self.current_goal_level,
            "objective": self.objective["goal"],
            "sub_goal": sg_description,
            "action_type": action.get("type"),
            "action_params": action.get("params", {}),
            "action_rationale": action.get("rationale", ""),
            "action_result_excerpt": result[:500],
            "fitness_status": fitness["status"],
            "fitness_score": fitness.get("score"),
            "fitness_reason": fitness.get("reason", ""),
            "fitness_evidence": fitness.get("evidence", ""),
            "capability_gained": fitness.get("capability_gained"),
            "stagnant_cycles": self.stagnant_cycles,
            "genome_mutated": False,
        }

        # 5. Apprentissage / Évolution
        if fitness["status"] == "PROGRESS":
            self.stagnant_cycles = 0
            memory_module.reinforce(action, result, fitness, self.genome)

        elif fitness["status"] in ("STAGNANT", "BLOCKED"):
            self.stagnant_cycles += 1

            if self.stagnant_cycles >= self.genome.get("stagnation_threshold", 5):
                print(f"\n[EVOLUTION] Stagnant for {self.stagnant_cycles} cycles — analyzing patterns...")
                stagnant_history = self.cycle_history[-self.stagnant_cycles:]
                reflection = reflect_module.analyze_history(stagnant_history, self.genome, self.objective)
                if reflection.get("patterns"):
                    print(f"  Reflection: {len(reflection['patterns'])} pattern(s), {len(reflection.get('proposals', []))} proposal(s)")
                print(f"  Mutating genome...")
                self.genome = evolver_module.mutate(self.genome, stagnant_history, self.objective, reflection={"patterns": reflection.get("patterns", []), "proposals": reflection.get("proposals", [])})
                self.stagnant_cycles = 0
                cycle_entry["genome_mutated"] = True
                audit.log_event("genome_mutation", {
                    "new_generation": self.genome["generation"],
                    "cycle_id": self.cycle_id,
                })

        elif fitness["status"] == "DONE":
            objective_module.mark_complete(self.objective, fitness.get("evidence", ""))
            audit.log_event("objective_completed", {
                "goal": self.objective["goal"],
                "cycles_taken": self.cycle_id,
                "genome_generation": self.genome["generation"],
                "phase": self.current_phase,
            })
            cycle_entry["objective_completed"] = True

            # En phase convert : vérifier le goal level avant d'avancer
            if self.current_phase == "convert":
                if self._check_convert_complete():
                    self._advance_phase(fitness)
                else:
                    # Phase pas encore complète — objectif complété mais level pas atteint
                    self.objective = None
                    self.current_sub_goal = None
                    self.stagnant_cycles = 0
            else:
                # Pour toutes les autres phases : DONE = phase complétée
                self._advance_phase(fitness)

        # 6. Avancer vers le prochain sous-but si besoin
        if fitness["status"] == "PROGRESS" and self.current_sub_goal:
            self._maybe_advance_sub_goal(fitness)

        # 7. Log + display + persist
        memory_module.record(cycle_entry)
        audit.log_cycle(cycle_entry)
        audit.print_cycle(cycle_entry)

        self.cycle_history.append(cycle_entry)
        self._save_session()

    def _advance_phase(self, fitness: dict):
        """
        Avance vers la phase suivante dans la spirale développementale.
        Après 'reflect' : incrémente le goal level et recommence à 'orient'.
        """
        phases = self.genome.get("developmental_phases", [])
        phase_ids = [p["id"] for p in phases]

        # Mettre à jour capability_inventory si le cycle a produit une nouvelle capacité
        capability_gained = fitness.get("capability_gained")
        if capability_gained:
            inv = self.genome.get("capability_inventory", {})
            inv[f"cap_{self.cycle_id}"] = {
                "description": capability_gained,
                "phase": self.current_phase,
                "goal_level": self.current_goal_level,
                "cycle": self.cycle_id,
            }
            self.genome["capability_inventory"] = inv
            genome_module.save(self.genome)
            print(f"\n  [CAPABILITY] New entry: {capability_gained[:80]}")

        # Déclencher une mutation de phase (apprendre de ce qui a marché)
        print(f"\n[PHASE COMPLETE] {self.current_phase.upper()} → mutating genome to consolidate learning...")
        phase_history = [c for c in self.cycle_history if c.get("phase") == self.current_phase]
        if phase_history:
            reflection = reflect_module.analyze_history(phase_history, self.genome, self.objective or {})
            self.genome = evolver_module.mutate(
                self.genome, phase_history, self.objective or {},
                reflection={"patterns": reflection.get("patterns", []), "proposals": reflection.get("proposals", [])}
            )

        # Enregistrer la phase complétée
        self.completed_phases.append(self.current_phase)
        audit.log_event("phase_completed", {
            "phase": self.current_phase,
            "goal_level": self.current_goal_level,
            "cycle_id": self.cycle_id,
        })

        # Phase suivante dans la spirale
        current_idx = phase_ids.index(self.current_phase) if self.current_phase in phase_ids else -1
        next_idx = current_idx + 1

        if next_idx >= len(phase_ids):
            # Fin du spiral courant (après reflect) → avancer le goal level
            self._advance_goal_level()
        else:
            self.current_phase = phase_ids[next_idx]
            self.genome["current_phase"] = self.current_phase
            genome_module.save(self.genome)
            print(f"\n[PHASE] → {self.current_phase.upper()}")

        # Réinitialiser l'objectif pour la nouvelle phase
        self.objective = None
        self.current_sub_goal = None
        self.completed_sub_goals = []
        self.stagnant_cycles = 0

    def _advance_goal_level(self):
        """
        Incrémente le goal level après la completion du spiral complet.
        Auto-génère le niveau suivant si nécessaire (×10).
        """
        self.current_goal_level += 1
        self.genome["current_goal_level"] = self.current_goal_level
        self.completed_phases = []  # reset pour le prochain spiral

        # Auto-générer le niveau suivant si absent
        ladder = self.genome.get("goal_ladder", [])
        if not any(g["level"] == self.current_goal_level for g in ladder):
            prev = next((g for g in ladder if g["level"] == self.current_goal_level - 1), {})
            prev_cents = prev.get("target_cents", 1000)
            new_cents = prev_cents * 10
            new_eur = new_cents // 100
            new_level = {
                "level": self.current_goal_level,
                "description": f"Earn €{new_eur} in real Stripe revenue",
                "target_cents": new_cents,
                "unlocks": f"level {self.current_goal_level + 1} reachable at {new_eur * 10}€",
                "verify_cmd": (
                    f"curl -s 'https://api.stripe.com/v1/balance_transactions?limit=100' "
                    f"-u $STRIPE_SECRET_KEY: | python3 -c \""
                    f"import sys,json; d=json.load(sys.stdin); "
                    f"total=sum(t['amount'] for t in d.get('data',[]) if t['status']=='available'); "
                    f"print('LEVEL_COMPLETE' if total>={new_cents} else f'PENDING {{total/100:.2f}}EUR')\""
                ),
            }
            ladder.append(new_level)
            self.genome["goal_ladder"] = ladder
            print(f"\n[GOAL LADDER] Level {self.current_goal_level} auto-generated: {new_level['description']}")

        # Restart spiral depuis 'orient'
        self.current_phase = "orient"
        self.genome["current_phase"] = "orient"
        genome_module.save(self.genome)

        audit.log_event("goal_level_advanced", {
            "new_level": self.current_goal_level,
            "cycle_id": self.cycle_id,
        })
        print(f"\n[GOAL LEVEL] → Level {self.current_goal_level} | Phase ORIENT (new spiral begins)")

    def _check_convert_complete(self) -> bool:
        """
        En phase convert : vérifie via verify_cmd si le goal level est atteint.
        Retourne True si LEVEL_COMPLETE.
        """
        ladder = self.genome.get("goal_ladder", [])
        current_goal = next((g for g in ladder if g["level"] == self.current_goal_level), None)
        if not current_goal or not current_goal.get("verify_cmd"):
            return False
        try:
            proc = subprocess.run(
                current_goal["verify_cmd"], shell=True,
                capture_output=True, text=True, timeout=30,
                env={**__import__("os").environ},
            )
            output = proc.stdout.strip()
            print(f"  [CONVERT CHECK] {output[:120]}")
            return "LEVEL_COMPLETE" in output
        except Exception as e:
            print(f"  [CONVERT CHECK ERROR] {e}")
            return False

    def _maybe_advance_sub_goal(self, fitness: dict):
        """Avance vers le prochain sous-but si le courant semble complété."""
        score = fitness.get("score", 0)
        if score >= 7:  # Score élevé = sous-but probablement terminé
            self.completed_sub_goals.append(self.current_sub_goal)
            remaining = [
                sg for sg in self.sub_goals
                if sg["id"] not in self.completed_sub_goals
            ]
            if remaining:
                self.current_sub_goal = remaining[0]["id"]
                print(f"\n  → Advanced to: {remaining[0].get('description', remaining[0]['id'])}")
            else:
                self.current_sub_goal = None

    def _blocked_cycle(self, sub_goal: str, reason: str):
        """
        Enregistre un cycle BLOCKED sans action réelle.
        Utilisé quand le LLM échoue à produire une réponse valide.
        """
        self.cycle_id += 1
        self.stagnant_cycles += 1

        cycle_entry = {
            "cycle_id": self.cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "genome_generation": self.genome["generation"],
            "objective": self.objective["goal"] if self.objective else "?",
            "sub_goal": sub_goal,
            "action_type": "none",
            "action_params": {},
            "action_rationale": "LLM error",
            "action_result_excerpt": "",
            "fitness_status": "BLOCKED",
            "fitness_score": 0,
            "fitness_reason": reason,
            "fitness_evidence": "",
            "stagnant_cycles": self.stagnant_cycles,
            "genome_mutated": False,
        }

        # Déclencher évolution si trop de cycles bloqués
        if self.stagnant_cycles >= self.genome.get("stagnation_threshold", 5):
            print(f"\n[EVOLUTION] Blocked for {self.stagnant_cycles} cycles — analyzing patterns...")
            stagnant_history = self.cycle_history[-self.stagnant_cycles:]
            reflection = reflect_module.analyze_history(stagnant_history, self.genome, self.objective or {})
            if reflection.get("patterns"):
                print(f"  Reflection: {len(reflection['patterns'])} pattern(s), {len(reflection.get('proposals', []))} proposal(s)")
            print(f"  Mutating genome...")
            self.genome = evolver_module.mutate(self.genome, stagnant_history, self.objective or {}, reflection={"patterns": reflection.get("patterns", []), "proposals": reflection.get("proposals", [])})
            self.stagnant_cycles = 0
            cycle_entry["genome_mutated"] = True
            audit.log_event("genome_mutation", {
                "new_generation": self.genome["generation"],
                "cycle_id": self.cycle_id,
                "trigger": "llm_error_loop",
            })

        memory_module.record(cycle_entry)
        audit.log_cycle(cycle_entry)
        audit.print_cycle(cycle_entry)
        self.cycle_history.append(cycle_entry)
        self._save_session()

        time.sleep(3)  # Pause avant retry

    def _handle_error_as_blocked_cycle(self, error: Exception):
        """
        Transforme une exception non gérée en cycle BLOCKED.
        Le kernel ne crash jamais — les erreurs font partie de l'évolution.
        """
        self.stagnant_cycles += 1

        audit.log_event("kernel_error", {
            "cycle_id": self.cycle_id,
            "stagnant_cycles": self.stagnant_cycles,
            "error": str(error),
            "traceback": traceback.format_exc(),
        })

        print(f"\n[BLOCKED] Cycle {self.cycle_id} error: {str(error)[:120]}")
        print(f"  Stagnant: {self.stagnant_cycles}/{self.genome.get('stagnation_threshold', 5)}")

        # Déclencher évolution si trop d'erreurs consécutives
        if (
            self.stagnant_cycles >= self.genome.get("stagnation_threshold", 5)
            and self.objective
        ):
            print(f"\n[EVOLUTION] Persistent errors — mutating genome...")
            try:
                stagnant_history = self.cycle_history[-self.stagnant_cycles:]
                self.genome = evolver_module.mutate(self.genome, stagnant_history, self.objective)
                self.stagnant_cycles = 0
                audit.log_event("genome_mutation", {
                    "new_generation": self.genome["generation"],
                    "cycle_id": self.cycle_id,
                    "trigger": "exception_loop",
                })
            except Exception as evolve_err:
                print(f"  [EVOLUTION FAILED] {evolve_err} — continuing anyway")

        time.sleep(min(5 * self.stagnant_cycles, 30))  # backoff progressif
