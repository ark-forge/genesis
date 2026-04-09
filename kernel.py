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

    def boot(self):
        """Initialise le kernel : charge génome, prépare workspace."""
        Path("/tmp/genesis_workspace").mkdir(parents=True, exist_ok=True)

        self.genome = genome_module.load()
        audit.log_event("kernel_boot", {
            "genome_generation": self.genome["generation"],
            "initial_objective": self.initial_objective,
        })
        print(f"\nGenesis booting... Generation {self.genome['generation']}")

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
                audit.log_event("kernel_error", {
                    "cycle_id": self.cycle_id,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                print(f"\n[ERROR] Cycle {self.cycle_id}: {e}")
                print("Continuing in 5s...")
                time.sleep(5)

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

        # 7. Log + display
        memory_module.record(cycle_entry)
        audit.log_cycle(cycle_entry)
        audit.print_cycle(cycle_entry)

        self.cycle_history.append(cycle_entry)

    def _maybe_advance_sub_goal(self, fitness: dict):
        """Avance vers le prochain sous-but si le courant semble complété."""
        score = fitness.get("score", 0)
        if score >= 7:  # Score élevé = sous-but probablement terminé
            self.completed_sub_goals.append(self.current_sub_goal)
            # Trouver le prochain sous-but non complété
            remaining = [
                sg for sg in self.sub_goals
                if sg["id"] not in self.completed_sub_goals
            ]
            if remaining:
                self.current_sub_goal = remaining[0]["id"]
                print(f"\n  → Advanced to: {remaining[0].get('description', remaining[0]['id'])}")
            else:
                # Tous les sous-buts complétés → re-décomposer ou finir
                self.current_sub_goal = None
