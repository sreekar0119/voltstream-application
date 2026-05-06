export const pageMotion = {
  initial: { opacity: 0, y: 16, filter: "blur(10px)" },
  animate: { opacity: 1, y: 0, filter: "blur(0px)" },
  exit: { opacity: 0, y: -8, filter: "blur(8px)" },
  transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] }
};

export const stagger = {
  animate: {
    transition: {
      staggerChildren: 0.07
    }
  }
};

export const lift = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.42 } }
};
