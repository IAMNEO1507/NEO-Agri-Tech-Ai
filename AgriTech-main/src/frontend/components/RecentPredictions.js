import {
  getPredictions,
  clearPredictions,
  comparePredictions
} from "../js/predictionStorage.js";

export default function RecentPredictions() {
  const history = getPredictions();

  const container = document.createElement("div");
  container.className = "recent-predictions";

  const title = document.createElement("h3");
  title.textContent = "Recent Predictions";
  container.appendChild(title);

  history.forEach((item, i) => {
  const div = document.createElement("div");
  div.className = "prediction-item";

  div.innerHTML = `
    <p><strong>${item.timestamp}</strong></p>
    <p>Input: ${item.input}</p>
    <p>Output: ${item.output}</p>
  `;

  const compareBtn = document.createElement("button");
  compareBtn.textContent = "Compare";

  compareBtn.onclick = () => {
    if (i + 1 < history.length) {
      const result = comparePredictions(i + 1, i);

      alert(
        `Previous Output: ${result.previous.output}
        Latest Output: ${result.latest.output}`
      );
    } else {
      alert("No previous prediction available");
    }
  };

  div.appendChild(compareBtn);

  container.appendChild(div);
});
  if (history.length > 0) {
    const clearBtn = document.createElement("button");
    clearBtn.textContent = "Clear History";
    clearBtn.onclick = () => {
      clearPredictions();
      container.innerHTML = "<p>No predictions yet.</p>";
    };
    container.appendChild(clearBtn);
  }

  return container;
}
