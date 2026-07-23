---
name: tailwind
description: Use when building or reviewing UI with Tailwind CSS — utility-first styling, responsive/state variants, design tokens via theme config, dark mode, and avoiding common anti-patterns. Applies to Next.js, React, and any Tailwind v3/v4 project.
---

# Tailwind CSS

Utility-first CSS conventions for building consistent, maintainable, accessible UI.
Pairs with the `google-labs-code/shadcn-ui` skill (shadcn/ui is built on Tailwind).

## Core principles

1. **Utilities first, custom CSS last.** Reach for `@apply` or hand-written CSS only
   when a pattern is genuinely reusable and utilities become unreadable. Prefer a
   component (React) over a CSS abstraction.
2. **Tokens, not magic numbers.** Drive spacing, color, radius, and typography from the
   theme (`tailwind.config` in v3, `@theme` in v4). Never hard-code hex colors or
   arbitrary `px` when a token exists. Arbitrary values (`w-[137px]`) are a smell —
   justify or tokenize them.
3. **Mobile-first.** Base styles target the smallest screen; layer breakpoints up
   (`sm: md: lg: xl: 2xl:`). Don't write desktop-first with `max-*` unless necessary.
4. **Compose, don't repeat.** Duplicated utility strings across elements → extract a
   component or use a variant helper (`cva`, `tailwind-variants`, or `clsx`/`cn`).

## Conventions

- **Class ordering:** follow the Prettier `prettier-plugin-tailwindcss` order
  (layout → box model → typography → visual → state). Install the plugin so ordering
  is automatic and diffs stay clean.
- **State & variants:** use `hover: focus-visible: active: disabled: aria-* data-*`
  variants rather than JS toggling of classes where possible. Always pair `hover:`
  affordances with `focus-visible:` for keyboard users.
- **Dark mode:** prefer the `dark:` variant with a `class` strategy (toggle `dark` on
  `<html>`), and define both light and dark token values. Don't ship light-only UI.
- **Conditional classes:** merge with a `cn()` helper (`clsx` + `tailwind-merge`) so
  later utilities correctly override earlier ones instead of both landing in the DOM.
- **Responsive layout:** prefer `flex`/`grid` + `gap-*` over margins for spacing between
  siblings. Use `container` queries (`@container`) for component-driven responsiveness in v4.

## Tailwind v4 notes

- Config moves into CSS: `@import "tailwindcss";` + `@theme { --color-brand: … }`.
- No `tailwind.config.js` required; content detection is automatic.
- Use CSS variables for tokens so runtime theming (multi-brand, user themes) is trivial.

## Accessibility & quality checklist

- [ ] Color contrast meets WCAG AA (don't rely on Tailwind's default palette blindly).
- [ ] Every interactive element has a visible `focus-visible:` state.
- [ ] No information conveyed by color alone.
- [ ] Respect `motion-reduce:` for animations/transitions.
- [ ] Class lists sorted (Prettier plugin) and duplicated patterns extracted.
- [ ] Arbitrary values justified; spacing/color/typography come from tokens.

## Anti-patterns to flag in review

- Inline hex/`rgb()` in `style={}` when a token exists.
- Long duplicated class strings copy-pasted across components.
- `!important` (`!`) utilities used to fight specificity instead of fixing ordering.
- Desktop-first `max-*` breakpoints for a mobile-first product.
- Toggling classes in JS where a `data-*`/`aria-*` variant would be declarative.
