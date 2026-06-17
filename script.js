const navLinks = Array.from(document.querySelectorAll(".nav a"));
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);
const heroTitle = document.querySelector("#hero-title");

if (heroTitle && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const text = heroTitle.dataset.typewriter || heroTitle.textContent;
  let index = 0;

  heroTitle.textContent = "";

  const typeNextCharacter = () => {
    heroTitle.textContent = text.slice(0, index);
    index += 1;

    if (index <= text.length) {
      window.setTimeout(typeNextCharacter, 42);
      return;
    }

    heroTitle.classList.add("typewriter-done");
  };

  window.setTimeout(typeNextCharacter, 260);
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }

      navLinks.forEach((link) => {
        const isActive = link.getAttribute("href") === `#${entry.target.id}`;
        link.classList.toggle("active", isActive);
      });
    });
  },
  { rootMargin: "-35% 0px -55% 0px", threshold: 0 }
);

sections.forEach((section) => observer.observe(section));
