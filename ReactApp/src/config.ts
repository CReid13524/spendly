import './env.d.ts'

const required = (value: string | undefined, name: string) => {
  if (!value) {
    throw new Error(`Missing environment variable: ${name}`);
  }
  return value;
};

export const config = {
  api: required(
    import.meta.env.VITE_API,
    'VITE_API'
  ),
};
