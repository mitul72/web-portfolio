import { STOPS } from "@/data/portfolio";
import { DialogueAction, Interactable, PROPS, propForSubPoi } from "@/data/interact";
import { useTour } from "./useTour";
import { useVoyage } from "./useVoyage";
import { greet, useInteract } from "./useInteract";

/**
 * Clicking a prop or an NPC. If the ship isn't already moored at that island
 * it sails there first; then the camera flies to the thing's close-up and its
 * content opens: the stop's or sub-POI's panel for a prop, the dialogue for
 * an NPC.
 */
export function activate(it: Interactable) {
  if (!it.stopId) {
    // the captain travels with the ship: just talk
    useInteract.getState().openDialogue(it.key.slice(4));
    return;
  }
  const index = STOPS.findIndex((s) => s.id === it.stopId);
  if (index < 0) return;
  const open = () => {
    const ui = useInteract.getState();
    const tour = useTour.getState();
    ui.focusShot(it.shot);
    if (it.kind === "npc") {
      tour.closePanel();
      ui.openDialogue(it.key.slice(4));
    } else {
      ui.closeDialogue();
      const sub = it.subPoi === null ? null : STOPS[index].subPois?.[it.subPoi];
      if (sub) tour.selectSubPoi(sub.id);
      else tour.openPanel();
    }
  };
  const here = useTour.getState().activeIndex === index && useVoyage.getState().phase === "docked";
  if (here) open();
  else useTour.getState().goTo(index, open);
}

/** A button in an NPC's dialogue. */
export function runDialogueAction(a: DialogueAction) {
  const ui = useInteract.getState();
  if (a.type === "close") {
    ui.closeDialogue();
    return;
  }
  if (a.type === "home") {
    ui.closeDialogue();
    useTour.getState().home();
    return;
  }
  if (a.type === "sail") {
    ui.closeDialogue();
    const index = STOPS.findIndex((s) => s.id === a.stopId);
    if (index >= 0) useTour.getState().goTo(index);
    return;
  }
  if (a.type === "sub") {
    const prop = propForSubPoi(a.stopId, a.index);
    if (prop) activate(prop);
    return;
  }
  // "stop": open the stop's own panel, at its prop's close-up
  const prop = Object.values(PROPS).find((p) => p.stopId === a.stopId && p.subPoi === null);
  if (prop) activate(prop);
  else {
    const index = STOPS.findIndex((s) => s.id === a.stopId);
    if (index >= 0) useTour.getState().goTo(index);
  }
}

/**
 * Close the content panel and hand back to the island's host, so exploring
 * an island is a loop: host -> a prop's content -> host -> the next one.
 */
export function closeToHost() {
  const tour = useTour.getState();
  tour.closePanel();
  if (tour.activeIndex === null || useVoyage.getState().phase !== "docked") return;
  greet(STOPS[tour.activeIndex].id);
}
