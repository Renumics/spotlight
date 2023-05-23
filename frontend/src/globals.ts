import React from 'react';
import ReactDOM from 'react-dom';
import styled from 'styled-components';
import * as lib from './lib';

// globals to be used by plugins
// Note: This can probably also be automatically generated during buildtime
//       We should probably figure that out some time and remove this file.

// React
globalThis.React = React;
globalThis.ReactDOM = ReactDOM;

// Styled Components
// eslint-disable-next-line
(globalThis as any).styled = styled;

// spotlight library for plugins
// eslint-disable-next-line
(globalThis as any).spotlight = lib;
