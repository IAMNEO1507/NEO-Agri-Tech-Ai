document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("crop-form");
  const resultContainer = document.getElementById("result-container");
  const resultText = document.getElementById("result-text");
  const guideContainer = document.getElementById("guide-container");
  const guideTitle = document.getElementById("guide-title");
  const guideTimeline = document.getElementById("guide-timeline");
  const guideHowToPlant = document.getElementById("guide-how-to-plant");
  const guideFertilizer = document.getElementById("guide-fertilizer");
  const guideIdealRainfall = document.getElementById("guide-ideal-rainfall");
  const guidePostHarvest = document.getElementById("guide-post-harvest");

  const cropProfiles = [
    {
      name: "Rice",
      pH: [5.5, 7.0],
      temperature: [20, 35],
      rainfall: [800, 1800],
      soils: ["Clay", "Black"],
      seasons: ["Monsoon"],
      irrigation: ["Canal", "Rainfed"],
      fertilizers: ["Urea+DAP", "NPK 10-26-26"],
      pests: ["Stem Borer"],
      demand: ["High"],
    },
    {
      name: "Wheat",
      pH: [6.0, 7.5],
      temperature: [15, 25],
      rainfall: [350, 700],
      soils: ["Loamy", "Clay"],
      seasons: ["Winter"],
      irrigation: ["Canal", "Sprinkler"],
      fertilizers: ["Urea+DAP", "NPK 10-26-26"],
      pests: ["Aphids"],
      demand: ["Medium", "High"],
    },
    {
      name: "Maize",
      pH: [5.8, 7.5],
      temperature: [18, 30],
      rainfall: [500, 1200],
      soils: ["Loamy", "Black"],
      seasons: ["Monsoon", "Summer"],
      irrigation: ["Sprinkler", "Canal"],
      fertilizers: ["Urea+DAP", "NPK 10-26-26"],
      pests: ["Bollworm", "Stem Borer"],
      demand: ["Medium"],
    },
    {
      name: "Cotton",
      pH: [6.0, 8.0],
      temperature: [21, 35],
      rainfall: [400, 900],
      soils: ["Black", "Clay"],
      seasons: ["Summer", "Monsoon"],
      irrigation: ["Drip", "Rainfed"],
      fertilizers: ["Urea+DAP", "NPK 10-26-26"],
      pests: ["Bollworm", "Aphids"],
      demand: ["High"],
    },
    {
      name: "Tomato",
      pH: [6.0, 7.0],
      temperature: [18, 30],
      rainfall: [400, 800],
      soils: ["Loamy", "Sandy", "Clay"],
      seasons: ["Winter", "Summer"],
      irrigation: ["Drip", "Sprinkler"],
      fertilizers: ["NPK 10-26-26", "Urea+DAP"],
      pests: ["Aphids", "Bollworm"],
      demand: ["High"],
    },
    {
      name: "Potato",
      pH: [5.0, 6.5],
      temperature: [15, 22],
      rainfall: [300, 600],
      soils: ["Loamy", "Sandy"],
      seasons: ["Winter"],
      irrigation: ["Sprinkler", "Drip"],
      fertilizers: ["NPK 10-26-26"],
      pests: ["Aphids"],
      demand: ["High", "Medium"],
    },
    {
      name: "Sugarcane",
      pH: [6.0, 8.0],
      temperature: [20, 35],
      rainfall: [800, 1500],
      soils: ["Black", "Clay", "Loamy"],
      seasons: ["Monsoon"],
      irrigation: ["Canal", "Drip"],
      fertilizers: ["Urea+DAP", "NPK 10-26-26"],
      pests: ["Stem Borer"],
      demand: ["High"],
    },
    {
      name: "Groundnut",
      pH: [5.5, 7.0],
      temperature: [20, 30],
      rainfall: [500, 1000],
      soils: ["Sandy", "Loamy"],
      seasons: ["Summer", "Monsoon"],
      irrigation: ["Drip", "Sprinkler"],
      fertilizers: ["Single Super Phosphate", "NPK 10-26-26"],
      pests: ["Aphids"],
      demand: ["Medium"],
    },
  ];

  function scoreRange(value, range, maxScore) {
    if (value >= range[0] && value <= range[1]) {
      return maxScore;
    }

    const gap = value < range[0] ? range[0] - value : value - range[1];
    return Math.max(0, maxScore - gap * (maxScore / 6));
  }

  function scoreMatch(value, options, maxScore) {
    return options.includes(value) ? maxScore : 0;
  }

  function buildTimeline(crop, season) {
    const timelines = {
      Rice: {
        Monsoon: "Plant: June-July | Harvest: October-November (110-140 days)",
        Summer: "Plant: Late spring | Harvest: Late summer (110-140 days)",
        Winter: "Plant: Not ideal for winter | Shift to a warm-season window",
      },
      Wheat: {
        Winter: "Plant: November-December | Harvest: March-April (110-130 days)",
        Monsoon: "Plant: Not ideal in monsoon | Wait for cool, dry weather",
        Summer: "Plant: Early summer only if irrigation is reliable",
      },
      Potato: {
        Winter: "Plant: October-November | Harvest: January-February (90-120 days)",
      },
      Tomato: {
        Winter: "Plant: August-October | Harvest: November-February (75-110 days)",
        Summer: "Plant: January-March | Harvest: April-June (75-110 days)",
      },
    };

    return (
      timelines[crop]?.[season] ||
      `Plant in the ${season.toLowerCase()} window best suited for ${crop}. | Harvest after the main growth cycle.`
    );
  }

  function buildGuide(crop, data, profile) {
    const plantingAdvice = {
      Rice:
        "Prepare a puddled seedbed, maintain standing water during establishment, and transplant healthy seedlings for better tillering.",
      Wheat:
        "Use a fine, firm seedbed and sow at the recommended spacing so the crop can establish before the coldest period.",
      Maize:
        "Sow on raised rows or beds for drainage, and maintain uniform spacing to support ear development.",
      Cotton:
        "Use well-prepared ridges or beds, sow at moderate depth, and avoid excess early moisture.",
      Tomato:
        "Transplant healthy seedlings into well-drained beds with staking or trellising to keep fruit off the ground.",
      Potato:
        "Plant disease-free seed tubers in ridges or furrows and keep soil loose for tuber expansion.",
      Sugarcane:
        "Plant setts in furrows with good soil moisture and keep rows wide enough for long-term cane growth.",
      Groundnut:
        "Sow on light, well-drained soil and keep the field weed-free during the first growth phase.",
    };

    const fertilizerAdvice = {
      Rice: "Begin with Urea + DAP, then top-dress after establishment to support tillering and grain fill.",
      Wheat: "Use Urea + DAP at sowing and a balanced NPK top-up during tillering if growth slows.",
      Maize: "Apply Urea + DAP early, then a nitrogen boost at knee-high stage for better cob formation.",
      Cotton: "Use Urea + DAP with split nitrogen applications to avoid excess vegetative growth.",
      Tomato: "Use NPK 10-26-26 early, then switch to a lighter nitrogen feed during flowering and fruiting.",
      Potato: "Use NPK 10-26-26 at planting and avoid overusing nitrogen to protect tuber quality.",
      Sugarcane: "Use Urea + DAP at planting and follow with split nitrogen applications through the season.",
      Groundnut: "Use Single Super Phosphate or a low-nitrogen starter mix to support pod development.",
    };

    return {
      title: `Complete Growing Guide for ${crop}`,
      timeline: buildTimeline(crop, data.Season),
      how_to_plant: plantingAdvice[crop] || `Prepare the field carefully and follow best agronomic spacing for ${crop}.`,
      fertilizer: fertilizerAdvice[crop] || `Use a balanced fertilizer plan matched to the nutrient needs of ${crop}.`,
      ideal_rainfall: `Target roughly ${profile.rainfall[0]}-${profile.rainfall[1]} mm of rainfall during the season. Match irrigation to soil moisture rather than a fixed schedule.`,
      post_harvest: `Harvest ${crop} at market-ready maturity, sort damaged produce quickly, and use cool, dry storage to reduce losses.`,
    };
  }

  function getCropRecommendation(data) {
    const cropScores = cropProfiles.map((profile) => {
      let score = 0;

      score += scoreRange(data.pH, profile.pH, 20);
      score += scoreRange(data.Temperature, profile.temperature, 20);
      score += scoreRange(data.Rainfall, profile.rainfall, 15);
      score += scoreMatch(data.Soil_Type, profile.soils, 10);
      score += scoreMatch(data.Season, profile.seasons, 10);
      score += scoreMatch(data.Irrigation_Method, profile.irrigation, 10);
      score += scoreMatch(data.Fertilizer_Used, profile.fertilizers, 5);
      score += scoreMatch(data.Market_Demand, profile.demand, 5);

      if (data.Pest_Issue && data.Pest_Issue !== "None") {
        score -= profile.pests.includes(data.Pest_Issue) ? 8 : 0;
      } else {
        score += 3;
      }

      return { profile, score };
    });

    cropScores.sort((a, b) => b.score - a.score);
    const bestMatch = cropScores[0].profile;
    return {
      crop: bestMatch.name,
      guide: buildGuide(bestMatch.name, data, bestMatch),
    };
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
      const el = document.getElementsByName(key)[0];
      data[key] = el.type === "number" ? parseFloat(value) : value;
    });

    // Show loading message
    displayLoading();
    window.__cropPlannerRenderPending = true;

    setTimeout(() => {
      try {
        const result = getCropRecommendation(data);
        displayResultAndGuide(result.crop, result.guide);
        showFeedback('Crop guide generated successfully!', 'success');
      } catch (error) {
        console.error("Error generating crop plan:", error);
        showFeedback('Could not generate a crop plan. Please review your inputs and try again.', 'error');
        displayError('Could not generate a crop plan. Please review your inputs and try again.');
      } finally {
        window.__cropPlannerRenderPending = false;
      }
    }, 600);
  });

  /**
   * Calls the Gemini API with exponential backoff.
   * @param {string} prompt The text prompt for the model.
   * @returns {Promise<object>} The parsed JSON response.
   */
  async function generateContentWithRetry(prompt, retries = 3, delay = 1000) {
    let chatHistory = [{ role: "user", parts: [{ text: prompt }] }];
    const payload = {
      contents: chatHistory,
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            crop: { type: "STRING" },
            guide: {
              type: "OBJECT",
              properties: {
                title: { type: "STRING" },
                timeline: { type: "STRING" },
                how_to_plant: { type: "STRING" },
                fertilizer: { type: "STRING" },
                ideal_rainfall: { type: "STRING" },
                post_harvest: { type: "STRING" },
              },
            },
          },
        },
      },
    };

    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (response.status === 429 && i < retries - 1) {
          await new Promise((res) => setTimeout(res, delay));
          delay *= 2; // Exponential backoff
          continue;
        }

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`API error: ${JSON.stringify(errorData)}`);
        }

        const result = await response.json();
        const jsonText = result?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) {
          throw new Error("Invalid response format from API.");
        }

        return JSON.parse(jsonText);
      } catch (error) {
        if (i === retries - 1) {
          console.error(
            "Failed to generate content after multiple retries:",
            error
          );
          throw error;
        }
      }
    }
  }

  /**
   * Displays a loading message in the result container.
   */
  function displayLoading() {
    resultContainer.classList.remove("hidden");
    resultText.textContent = "Curating your personalized crop guide...";
    guideContainer.classList.add("hidden");
  }

  /**
   * Displays an error message in the result container.
   * @param {string} message The error message to display.
   */
  function displayError(message) {
    resultContainer.classList.remove("hidden");
    resultText.textContent = message;
    guideContainer.classList.add("hidden");
    showFeedback(message, 'error');
  }

  /**
   * Simple function to convert basic markdown (like **bold**) to HTML.
   * @param {string} text The text to format.
   * @returns {string} The formatted HTML string.
   */
  function formatAIResponse(text) {
    if (!text) return "";
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    formattedText = formattedText.replace(/\n/g, "<br>");
    return formattedText;
  }

  /**
   * Populates the result and guide sections with the API response.
   * @param {string} cropName The recommended crop name.
   * @param {object} guide The guide object from the API response.
   */
  function displayResultAndGuide(cropName, guide) {
    resultContainer.classList.remove("hidden");
    resultText.textContent = cropName;

    guideTitle.textContent = guide.title;

    // Use the new formatting function and .innerHTML
    guideTimeline.innerHTML = formatAIResponse(guide.timeline);
    guideHowToPlant.innerHTML = formatAIResponse(guide.how_to_plant);
    guideFertilizer.innerHTML = formatAIResponse(guide.fertilizer);
    guideIdealRainfall.innerHTML = formatAIResponse(guide.ideal_rainfall);
    guidePostHarvest.innerHTML = formatAIResponse(guide.post_harvest);

    guideContainer.classList.remove("hidden");
  }
});

let scene, camera, renderer, particles;

function initThreeJS() {
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.z = 50;

  renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById("three-canvas"),
    alpha: true,
    antialias: true,
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x000000, 0);

  createParticles();

  animate();

  window.addEventListener("resize", onWindowResize);
}

function createParticles() {
  const geometry = new THREE.BufferGeometry();
  const particleCount = 100;

  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  const greenColor = new THREE.Color(0x2e7d32);
  const lightGreenColor = new THREE.Color(0x4caf50);

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3;

    positions[i3] = (Math.random() - 0.5) * 200;
    positions[i3 + 1] = (Math.random() - 0.5) * 200;
    positions[i3 + 2] = (Math.random() - 0.5) * 100;

    const color = Math.random() > 0.5 ? greenColor : lightGreenColor;
    colors[i3] = color.r;
    colors[i3 + 1] = color.g;
    colors[i3 + 2] = color.b;
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: 2,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
  });

  particles = new THREE.Points(geometry, material);
  miniScene.add(particles);
}
function centerAndScale(object, targetSize = 3) {
  const box = new THREE.Box3().setFromObject(object);
  const size = new THREE.Vector3();
  box.getSize(size);

  const maxDim = Math.max(size.x, size.y, size.z);
  const scale = targetSize / maxDim;

  object.scale.setScalar(scale);

  const center = new THREE.Vector3();
  box.getCenter(center);
  object.position.sub(center.multiplyScalar(scale));
}

function animate() {
  requestAnimationFrame(animate);

  if (particles) {
    particles.rotation.x += 0.001;
    particles.rotation.y += 0.002;
  }
  miniRenderer.render(miniScene, miniCamera);


}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.addEventListener("load", initThreeJS);

const form = document.getElementById("crop-form");
const progressBar = document.getElementById("progress-bar");
const submitBtn = document.getElementById("submit-btn");
const resultContainer = document.getElementById("result-container");

function updateProgress() {
  const inputs = form.querySelectorAll("input[required], select[required]");
  const filled = Array.from(inputs).filter(
    (input) => input.value.trim() !== ""
  ).length;
  const progress = (filled / inputs.length) * 100;
  progressBar.style.width = progress + "%";
}

form.addEventListener("input", updateProgress);
form.addEventListener("change", updateProgress);

function validateField(field) {
  const formGroup = field.closest(".form-group");
  const isValid = field.value.trim() !== "" && field.checkValidity();

  formGroup.classList.remove("error", "success");
  if (field.value.trim() !== "") {
    formGroup.classList.add(isValid ? "success" : "error");
  }

  return isValid;
}

form.querySelectorAll("input, select").forEach((field) => {
  field.addEventListener("blur", () => validateField(field));
  field.addEventListener("input", () => {
    if (field.closest(".form-group").classList.contains("error")) {
      validateField(field);
    }
  });
});

form.addEventListener("submit", function (e) {
  if (window.__cropPlannerRenderPending) {
    return;
  }

  e.preventDefault();
  return;
});

updateProgress();

let lastScrollTop = 0;
const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

  if (scrollTop > lastScrollTop && scrollTop > 100) {
    navbar.style.transform = "translateY(-100%)";
  } else {
    navbar.style.transform = "translateY(0)";
  }

  lastScrollTop = scrollTop;
});
