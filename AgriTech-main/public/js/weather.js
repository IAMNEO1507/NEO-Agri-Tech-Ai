key = "005186776a4c4589a6e90608250407";
url = "https://api.weatherapi.com/v1";

const locationInput = document.getElementById('cityInput');
const searchButton = document.getElementById('search');
const getCity = document.getElementById('city');
const getRegion = document.getElementById('region');
const getCountry = document.getElementById('country');
const getTemperature = document.getElementById('temperature');
const getDescription = document.getElementById('description');
const suggestionsDropdown = document.getElementById('suggestions');

let debounceTimer;
let selectedSuggestionIndex = -1;

// Default city
window.onload = () => {
    fetchWeather("New Delhi");
}

// City autocomplete functionality
locationInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    
    clearTimeout(debounceTimer);
    
    if (query.length < 2) {
        hideSuggestions();
        return;
    }
    
    debounceTimer = setTimeout(() => {
        fetchCitySuggestions(query);
    }, 400);
});

// Keyboard navigation for suggestions
locationInput.addEventListener('keydown', (e) => {
    const suggestionItems = suggestionsDropdown.querySelectorAll('.suggestion-item');
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestionItems.length - 1);
        updateSelectedSuggestion(suggestionItems);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
        updateSelectedSuggestion(suggestionItems);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (selectedSuggestionIndex >= 0 && suggestionItems[selectedSuggestionIndex]) {
            suggestionItems[selectedSuggestionIndex].click();
        } else {
            searchButton.click();
        }
    } else if (e.key === 'Escape') {
        hideSuggestions();
    }
});

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        hideSuggestions();
    }
});

async function fetchCitySuggestions(query) {
    const searchURL = `${url}/search.json?key=${key}&q=${query}`;
    
    try {
        const response = await fetch(searchURL);
        if (response.ok) {
            const data = await response.json();
            displaySuggestions(data);
        }
    } catch (error) {
        console.log("Error fetching city suggestions", error);
    }
}

function displaySuggestions(cities) {
    suggestionsDropdown.innerHTML = '';
    selectedSuggestionIndex = -1;
    
    if (cities.length === 0) {
        suggestionsDropdown.innerHTML = '<div class="no-suggestions">No cities found</div>';
        suggestionsDropdown.classList.add('show');
        return;
    }
    
    cities.forEach((city) => {
        const suggestionItem = document.createElement('div');
        suggestionItem.classList.add('suggestion-item');
        
        const cityDetails = [city.region, city.country].filter(Boolean).join(', ');
        
        suggestionItem.innerHTML = `
            <div class="city-name">${city.name}</div>
            <div class="city-details">${cityDetails}</div>
        `;
        
        suggestionItem.addEventListener('click', () => {
            locationInput.value = city.name;
            hideSuggestions();
            fetchWeather(city.name);
        });
        
        suggestionsDropdown.appendChild(suggestionItem);
    });
    
    suggestionsDropdown.classList.add('show');
}

function updateSelectedSuggestion(items) {
    items.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.style.backgroundColor = '#f0f8ff';
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.style.backgroundColor = '';
        }
    });
}

function hideSuggestions() {
    suggestionsDropdown.classList.remove('show');
    suggestionsDropdown.innerHTML = '';
    selectedSuggestionIndex = -1;
}

// Dynamic background
function updateBackground(conditionText) {
    const body = document.body;
    let imageUrl = '';

    const lowerCaseCondition = conditionText.toLowerCase();

    if (lowerCaseCondition.includes('sunny') || lowerCaseCondition.includes('clear') || lowerCaseCondition.includes('sun')) {
        imageUrl = 'https://images.unsplash.com/photo-1504386106331-3e4e71712b38?q=80&w=1920';
    } else if (lowerCaseCondition.includes('cloudy') || lowerCaseCondition.includes('overcast') || lowerCaseCondition.includes('mist') || lowerCaseCondition.includes('cloud') || lowerCaseCondition.includes('haze')) {
        imageUrl = 'https://images.unsplash.com/photo-1483702721041-b23de737a886?q=80&w=1920';
    } else if (lowerCaseCondition.includes('rain') || lowerCaseCondition.includes('drizzle') || lowerCaseCondition.includes('shower') || lowerCaseCondition.includes('rainy')) {
        imageUrl = 'https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?q=80&w=1920';
    } else if (lowerCaseCondition.includes('snow') || lowerCaseCondition.includes('sleet') || lowerCaseCondition.includes('ice') || lowerCaseCondition.includes('snowy')) {
        imageUrl = 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?q=80&w=1920';
    } else if (lowerCaseCondition.includes('thunder') || lowerCaseCondition.includes('storm') || lowerCaseCondition.includes('thundery') || lowerCaseCondition.includes('stormy')) {
        imageUrl = 'https://images.unsplash.com/photo-1492011221367-f47e3ccd77a0?q=80&w=1920';
    } else if (lowerCaseCondition.includes('fog') || lowerCaseCondition.includes('foggy') || lowerCaseCondition.includes('dew') || lowerCaseCondition.includes('dewy')) {
        imageUrl = 'https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?q=80&w=1920';
    } else {
        imageUrl = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=1920';
    }

    body.style.backgroundImage = `url('${imageUrl}')`;
    body.style.backgroundSize = 'cover';
    body.style.backgroundPosition = 'center';
    body.style.backgroundRepeat = 'no-repeat';
    body.style.backgroundAttachment = 'fixed';
}

searchButton.addEventListener('click', () => {
    const location = locationInput.value;
    if (location) {
        fetchWeather(location);
        hideSuggestions();
    }
});

locationInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && selectedSuggestionIndex === -1) {
        searchButton.click();
    }
});

async function fetchWeather(location) {
    // Single optimized fetch for current, hourly, and 10 days forecast data
    const forecastURL = `${url}/forecast.json?key=${key}&q=${location}&days=10`;

    try {
        const response = await fetch(forecastURL);
        if (response.ok) {
            const data = await response.json();
            displayWeather(data);
            displayHourlyForecast(data);
            displayDaywiseForecast(data);
            updateBackground(data.current.condition.text);
        } else {
            console.log("Weather API returned an error:", response.status);
        }
    } catch (error) {
        console.log("Error fetching weather data:", error);
    }
}

// General data
function displayWeather(data) {
    const generalContainer = document.querySelector('.general');
    
    // Trigger smooth fade-in animation
    generalContainer.classList.remove('fade-in');
    void generalContainer.offsetWidth; // trigger reflow
    generalContainer.classList.add('fade-in');

    getCity.textContent = data.location.name;
    getRegion.textContent = data.location.region;
    getCountry.textContent = data.location.country;
    getTemperature.innerHTML = `${data.current.temp_c}°C <img src="https:${data.current.condition.icon}" alt="${data.current.condition.text}" />`;
    getDescription.textContent = data.current.condition.text;
}

// Hourly weather data
function displayHourlyForecast(data) {
    const hourlyForecastContainer = document.getElementById('hour');
    hourlyForecastContainer.innerHTML = '';
    const todayHourlyForecast = data.forecast.forecastday[0].hour;

    const currentHour = new Date(data.location.localtime).getHours();
    let cardCount = 0;

    todayHourlyForecast.forEach(hourData => {
        const hour = new Date(hourData.time).getHours();

        if (hour > currentHour) {
            const hourlyCard = document.createElement('div');
            hourlyCard.classList.add('hData-card', 'fade-in');
            hourlyCard.style.animationDelay = `${cardCount * 0.04}s`;
            
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const formattedHour = hour % 12 === 0 ? 12 : hour % 12;

            hourlyCard.innerHTML = `
                <p class="time">${formattedHour} ${ampm}</p>
                <img src="https:${hourData.condition.icon}" alt="${hourData.condition.text}" />
                <p class="temp">${hourData.temp_c}°C</p>
            `;
            hourlyForecastContainer.appendChild(hourlyCard);
            cardCount++;
        }
    });

    // Fallback if checked late at night, display next day's early hours
    if (cardCount === 0 && data.forecast.forecastday[1]) {
        const tomorrowHourlyForecast = data.forecast.forecastday[1].hour;
        tomorrowHourlyForecast.slice(0, 12).forEach((hourData, idx) => {
            const hour = new Date(hourData.time).getHours();
            const hourlyCard = document.createElement('div');
            hourlyCard.classList.add('hData-card', 'fade-in');
            hourlyCard.style.animationDelay = `${idx * 0.04}s`;
            
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const formattedHour = hour % 12 === 0 ? 12 : hour % 12;

            hourlyCard.innerHTML = `
                <p class="time">Tom. ${formattedHour} ${ampm}</p>
                <img src="https:${hourData.condition.icon}" alt="${hourData.condition.text}" />
                <p class="temp">${hourData.temp_c}°C</p>
            `;
            hourlyForecastContainer.appendChild(hourlyCard);
        });
    }
}

// Daywise weather
function displayDaywiseForecast(data) {
    const dayWiseForecastContainer = document.getElementById('day');
    dayWiseForecastContainer.innerHTML = '';
    const forecastCollection = data.forecast.forecastday;

    forecastCollection.forEach((forecastData, index) => {
        const forecastCard = document.createElement('div');
        forecastCard.classList.add('dayData-card', 'fade-in');
        forecastCard.style.animationDelay = `${index * 0.04}s`;

        const dateObj = new Date(forecastData.date);
        const options = { weekday: 'short', month: 'short', day: 'numeric' };
        let formattedDate = dateObj.toLocaleDateString('en-US', options);

        const today = new Date().toDateString();
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (dateObj.toDateString() === today) {
            formattedDate = 'Today';
        } else if (dateObj.toDateString() === tomorrow.toDateString()) {
            formattedDate = 'Tomorrow';
        }

        forecastCard.innerHTML = `
            <p class="date">${formattedDate}</p>
            <img src="https:${forecastData.day.condition.icon}" alt="${forecastData.day.condition.text}" />
            <p class="temp">
                <span style="font-weight: 700; color: var(--text-primary);">${forecastData.day.maxtemp_c}°C</span> 
                <span style="font-weight: 400; color: var(--text-muted); margin-left: 8px;">${forecastData.day.mintemp_c}°C</span>
            </p>
        `;
        dayWiseForecastContainer.appendChild(forecastCard);
    });
}
