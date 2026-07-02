export function toggleItem<T>(list: T[], item: T): T[] {
  const selected = new Set(list);

  if (selected.has(item)) {
    selected.delete(item);
  } else {
    selected.add(item);
  }

  return [...selected];
}
