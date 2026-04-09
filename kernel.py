"""
Kernel — Boucle cognitive principale de Genesis.

Flux : generate_objective → decompose → think → act → assess → evolve/learn → loop
"""

import json
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

        if restored:
            print(f"\nGenesis resuming... Generation {self.genome['generation']} | Cycle {self.cycle_id} | Objective: {self.objective['goal'][:60]}...")
        else:
            print(f"\nGenesis booting fresh... Generation {self.genome['generation']}")

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
        """Génère ou adopte l'objectif initial."""
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
            }
        else:
            # Auto-génération
            print("\nGenerating autonomous objective...")
            self.objective = objective_module.generate(self.genome, memory_ctx)

        self.completed_sub_goals = []
        audit.log_event("objective_acquired", {
            "goal": self.objective["goal"],
            "genome_generation": self.genome["generation"],
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

    def _run_cycle(self):
        """Exécute un cycle complet : think → act → assess → evolve/learn."""
        self.cycle_id += 1

        # Contexte mémoire
        memory_ctx = memory_module.get_context(self.objective)

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

            # 3d. Évaluer la fitness
            fitness = fitness_module.assess(
                objective=self.objective,
                sub_goal=sg_description,
                action_taken=action,
                action_result=result,
                cycle_history=self.cycle_history,
                genome=self.genome,
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
                print(f"\n[EVOLUTION] Stagnant for {self.stagnant_cycles} cycles — mutating genome...")
                stagnant_history = self.cycle_history[-self.stagnant_cycles:]
                self.genome = evolver_module.mutate(self.genome, stagnant_history, self.objective)
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
            })
            self.objective = None
            self.current_sub_goal = None
            self.stagnant_cycles = 0
            cycle_entry["objective_completed"] = True

        # 6. Avancer vers le prochain sous-but si besoin
        if fitness["status"] == "PROGRESS" and self.current_sub_goal:
            self._maybe_advance_sub_goal(fitness)

        # 7. Log + display + persist
        memory_module.record(cycle_entry)
        audit.log_cycle(cycle_entry)
        audit.print_cycle(cycle_entry)

        self.cycle_history.append(cycle_entry)
        self._save_session()

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
            print(f"\n[EVOLUTION] Blocked for {self.stagnant_cycles} cycles — mutating genome...")
            stagnant_history = self.cycle_history[-self.stagnant_cycles:]
            self.genome = evolver_module.mutate(self.genome, stagnant_history, self.objective or {})
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
