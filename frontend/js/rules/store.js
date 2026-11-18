export const STORAGE_KEY = 'fairExam.v2';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function createStore(storage, seed) {
  return {
    load() {
      const raw = storage.getItem(STORAGE_KEY);
      if (raw) {
        try {
          return JSON.parse(raw);
        } catch {
          // Unreadable saved state: fall back to the seed.
        }
      }
      return clone(seed);
    },
    save(state) {
      storage.setItem(STORAGE_KEY, JSON.stringify(state));
    },
  };
}
