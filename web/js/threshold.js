// HTTP thresholds are percentages. Explicit units distinguish intentional
// sub-1% settings from a CLI fraction accidentally copied into the request.
export function allinThresholdPercent(value) {
  return value !== null && typeof value === 'object' ? value.percent : value;
}

export function allinThresholdRequest(percent) {
  return percent > 0 && percent < 1 ? { percent } : percent;
}
