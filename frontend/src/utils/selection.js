export function toggleItem(list, item) {
  const selected = new Set(list);

  if (selected.has(item)) {
    selected.delete(item);
  } else {
    selected.add(item);
  }

  return [...selected];
}
