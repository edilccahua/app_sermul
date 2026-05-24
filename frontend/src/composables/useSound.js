/**
 * useSound — Composable de feedback sonoro para ventanilla de almacén
 *
 * Reproduce success.wav o error.wav desde /public/sounds/.
 * El .catch(() => {}) previene errores en browsers que bloquean
 * autoplay sin interacción previa del usuario.
 */

export function useSound() {
  function playSuccess() {
    new Audio('/sounds/success.wav').play().catch(() => {})
  }

  function playError() {
    new Audio('/sounds/error.wav').play().catch(() => {})
  }

  return { playSuccess, playError }
}
