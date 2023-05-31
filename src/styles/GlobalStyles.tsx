import { createGlobalStyle } from 'styled-components';
import tw, { GlobalStyles as BaseStyles } from 'twin.macro';

const CustomStyles = createGlobalStyle`
  body {
    ${tw`antialiased overflow-hidden`}
  }

  .Toastify__toast-container {
      width: auto !important;
      max-width: 500px;
  }

  input {
      user-select: text;
      -webkit-user-select: text; /* Chrome all / Safari all */
      -moz-user-select: text; /* Firefox all */
      -ms-user-select: text; /* IE 10+ */
  }
`;

const GlobalStyles = (): JSX.Element => (
    <>
        <BaseStyles />
        <CustomStyles />
    </>
);

export default GlobalStyles;
