// genre numbers from the proto enum
export const GENRES = [
  { value: 1, label: "Fiction" },
  { value: 2, label: "Non-fiction" },
  { value: 3, label: "Mystery" },
  { value: 4, label: "Science fiction" },
  { value: 5, label: "Fantasy" },
  { value: 6, label: "Biography" },
  { value: 7, label: "History" },
  { value: 8, label: "Romance" },
  { value: 9, label: "Thriller" },
  { value: 10, label: "Children" },
  { value: 11, label: "Other" },
];

export function getGenreLabel(genre) {
  for (let i = 0; i < GENRES.length; i++) {
    if (GENRES[i].value === genre) {
      return GENRES[i].label;
    }
  }
  return "Unknown";
}

// protobuf timestamp -> readable string
export function formatTime(ts) {
  if (!ts || !ts.seconds) {
    return "-";
  }
  const ms = Number(ts.seconds) * 1000;
  return new Date(ms).toLocaleString();
}
