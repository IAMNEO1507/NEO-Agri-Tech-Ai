export function savePrediction(input, output) {
  const history = JSON.parse(localStorage.getItem("predictions")) || [];
  const newEntry = { input, output, timestamp: new Date().toLocaleString() };
  history.unshift(newEntry);
  localStorage.setItem("predictions", JSON.stringify(history.slice(0, 5)));
}

export function getPredictions() {
  return JSON.parse(localStorage.getItem("predictions")) || [];
}

export function clearPredictions() {
  localStorage.removeItem("predictions");
}
export function comparePredictions(index1, index2) {
  const history = getPredictions();

  return {
    previous: history[index1],
    latest: history[index2]
  };
}
