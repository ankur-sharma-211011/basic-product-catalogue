
const area = document.getElementById("products");
const search = document.getElementById("search");
const category = document.getElementById("category");
const dialog = document.getElementById("details");

const themeControl = document.getElementById("theme");
const accentControl = document.getElementById("accent");
const fontControl = document.getElementById("fontSize");
const radiusControl = document.getElementById("cardRadius");
const resetButton = document.getElementById("resetAppearance");

const root = document.documentElement;

const defaultSettings = {
    theme: "light",
    accent: "#2563a6",
    fontSize: "16px",
    cardRadius: "9px"
};

// Apply appearance settings to the website.
function applyAppearance(settings) {
    root.dataset.theme = settings.theme;

    root.style.setProperty(
        "--accent-color",
        settings.accent
    );

    root.style.setProperty(
        "--font-size",
        settings.fontSize
    );

    root.style.setProperty(
        "--card-radius",
        settings.cardRadius
    );
}

// Save appearance settings in the browser.
function saveAppearance() {
    const settings = {
        theme: themeControl.value,
        accent: accentControl.value,
        fontSize: fontControl.value,
        cardRadius: radiusControl.value
    };

    applyAppearance(settings);

    localStorage.setItem(
        "appearanceSettings",
        JSON.stringify(settings)
    );
}

// Load previously saved settings.
function loadAppearance() {
    let settings = defaultSettings;

    try {
        const saved = localStorage.getItem("appearanceSettings");

        if (saved) {
            const parsed = JSON.parse(saved);

            // Only accept supported values.
            settings = {
                theme: ["light", "dark", "warm"].includes(parsed.theme)
                    ? parsed.theme : defaultSettings.theme,

                accent: /^#[0-9a-fA-F]{6}$/.test(parsed.accent)
                    ? parsed.accent : defaultSettings.accent,

                fontSize: ["14px", "16px", "18px"].includes(parsed.fontSize)
                    ? parsed.fontSize : defaultSettings.fontSize,

                cardRadius: ["0px", "9px", "20px"].includes(parsed.cardRadius)
                    ? parsed.cardRadius : defaultSettings.cardRadius
            };
        }
    } catch {
        settings = defaultSettings;
    }

    themeControl.value = settings.theme;
    accentControl.value = settings.accent;
    fontControl.value = settings.fontSize;
    radiusControl.value = settings.cardRadius;

    applyAppearance(settings);
}

// Reset to original appearance.
function resetAppearance() {
    themeControl.value = defaultSettings.theme;
    accentControl.value = defaultSettings.accent;
    fontControl.value = defaultSettings.fontSize;
    radiusControl.value = defaultSettings.cardRadius;

    saveAppearance();
}

// Load product categories.
async function loadCategories() {
    try {
        const response = await fetch("/api/categories");

        if (!response.ok) {
            throw new Error("Could not load categories");
        }

        const categories = await response.json();

        categories.forEach((c) => {
            const option = document.createElement("option");
            option.value = c;
            option.textContent = c;
            category.appendChild(option);
        });
    } catch (error) {
        console.error(error);
    }
}

// Load products using current search and category filters.
async function loadProducts() {
    try {
        const params = new URLSearchParams({
            search: search.value,
            category: category.value
        });

        const response = await fetch("/api/products?" + params);

        if (!response.ok) {
            throw new Error("Could not load products");
        }

        const items = await response.json();

        area.replaceChildren();

        if (!items.length) {
            const message = document.createElement("p");
            message.className = "empty";
            message.textContent = "No products found.";
            area.appendChild(message);
            return;
        }

        items.forEach((p) => {
            const card = document.createElement("article");
            card.className = "card";

            const picture = document.createElement("div");
            picture.className = "picture";
            picture.textContent = "🛍️";

            const productCategory = document.createElement("div");
            productCategory.className = "category";
            productCategory.textContent = p.category;

            const name = document.createElement("h3");
            name.textContent = p.name;

            const price = document.createElement("div");
            price.className = "price";
            price.textContent =
                "₹" + Number(p.price).toLocaleString("en-IN");

            const button = document.createElement("button");
            button.textContent = "View details";

            button.addEventListener("click", () => {
                showDetails(p.id);
            });

            card.append(
                picture,
                productCategory,
                name,
                price,
                button
            );

            area.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        area.textContent = "Unable to load products.";
    }
}

// Show product details.
async function showDetails(id) {
    try {
        const response = await fetch("/api/products/" + id);

        if (!response.ok) return;

        const p = await response.json();

        const content = document.getElementById("details-content");
        content.replaceChildren();

        const title = document.createElement("h2");
        title.textContent = p.name;

        const categoryText = document.createElement("p");
        categoryText.textContent = "Category: " + p.category;

        const priceText = document.createElement("p");
        priceText.textContent =
            "Price: ₹" + Number(p.price).toLocaleString("en-IN");

        const stockText = document.createElement("p");
        stockText.textContent = "Available stock: " + p.stock;

        const description = document.createElement("p");
        description.textContent = p.description;

        content.append(
            title,
            categoryText,
            priceText,
            stockText,
            description
        );

        dialog.showModal();

    } catch (error) {
        console.error(error);
    }
}

// Live appearance controls.
themeControl.addEventListener("change", saveAppearance);
accentControl.addEventListener("input", saveAppearance);
fontControl.addEventListener("change", saveAppearance);
radiusControl.addEventListener("change", saveAppearance);
resetButton.addEventListener("click", resetAppearance);

// Existing catalogue controls.
search.addEventListener("input", loadProducts);
category.addEventListener("change", loadProducts);

document.getElementById("closeDetails").addEventListener("click", () => {
    dialog.close();
});

// Initialize the website.
loadAppearance();
loadCategories().then(loadProducts);
