// import more2Image from 'flexlayout-react/images/more2.png';

import tw, { styled } from 'twin.macro';

const Styles = styled.div`
    .flexlayout__layout {
        ${tw`absolute inset-0 overflow-hidden`}
    }

    .flexlayout__splitter {
        ${tw`bg-gray-400`}
    }
    .flexlayout__splitter_vert:after {
        ${tw`absolute top-0 bottom-0 -left-1 -right-1 bg-transparent [content:'']`}
    }
    .flexlayout__splitter_horz:after {
        ${tw`absolute -top-1 -bottom-1 left-0 -right-0 bg-transparent [content:'']`}
    }
    @media (hover: hover) {
        .flexlayout__splitter:hover {
            ${tw`bg-gray-500 z-10`}
        }
    }
    .flexlayout__splitter_border {
        ${tw`z-10`}
    }
    .flexlayout__splitter_drag {
        ${tw`bg-blue-600 [z-index:'1000']`}
    }

    .flexlayout__outline_rect {
        ${tw`absolute border-2 border-blue-600 bg-blue-600 bg-opacity-10 cursor-move [z-index:'1000']`}
    }
    .flexlayout__outline_rect_edge {
        ${tw`border-2 border-blue-300 bg-blue-300 bg-opacity-10 cursor-move [z-index:'1000']`}
    }
    .flexlayout__edge_rect {
        ${tw`absolute bg-blue-600 [z-index:'1000']`}
    }
    .flexlayout__drag_rect {
        ${tw`absolute flex flex-col cursor-move text-sm text-midnight-600 font-semibold
            border border-gray-400 bg-gray-100 [z-index:'1000'] overflow-hidden pl-2 pr-5 py-0.5 text-center justify-center break-words`};
    }
    .flexlayout__tabset {
        ${tw`bg-gray-200 overflow-hidden`};
    }
    .flexlayout__tabset_header {
        ${tw`absolute flex items-center left-0 right-0 py-3 pr-3 pl-5 left-0 right-0`}
    }
    .flexlayout__tabset_header_content {
        ${tw`flex-grow`}
    }
    .flexlayout__tabset_tabbar_outer {
        ${tw`absolute flex left-0 right-0`}
    }
    .flexlayout__tabset_tabbar_outer_top {
        ${tw`border-b border-gray-400`}
    }
    .flexlayout__tabset_tabbar_outer_bottom {
    }
    .flexlayout__tabset_tabbar_inner {
        ${tw`relative flex flex-grow`}
    }
    .flexlayout__tabset_tabbar_inner_tab_container {
        ${tw`absolute flex top-0 bottom-0 [width:'10000px']`}
    }
    .flexlayout__tabset_tabbar_inner_tab_container_top {
    }
    .flexlayout__tabset_tabbar_inner_tab_container_bottom {
    }
    .flexlayout__tabset-selected {
        ${tw`bg-gray-200`}
    }
    .flexlayout__tabset-maximized {
        ${tw`bg-gray-200`}
    }
    .flexlayout__tab {
        ${tw`absolute overflow-auto bg-gray-100`}
    }
    .flexlayout__tab_button {
        ${tw`
            flex
            items-center
            text-sm
            cursor-pointer
            transition
            border-r
        `}
    }
    .flexlayout__tab_button--selected {
        ${tw`
            bg-gray-100
            text-midnight-600 font-semibold
            border-gray-300
            border-b border-b-gray-200 [margin-bottom:-1px]
        `}
    }
    .flexlayout__tab_button--unselected {
        ${tw`
            bg-gray-200
            text-navy-600 hover:text-blue-600
            border-gray-400
        `}
    }
    .flexlayout__tab_button_leading {
        ${tw`inline-block pr-2`}
    }
    .flexlayout__tab_button_content {
        ${tw`inline-block whitespace-nowrap truncate opacity-100 pl-1`}
    }
    .flexlayout__tab_button_textbox {
        ${tw`bg-white text-black font-semibold focus:ring ring-blue-300 outline-none`}
    }
    .flexlayout__tab_button_trailing {
        ${tw`flex justify-center items-center  w-5 h-5 opacity-30 hover:opacity-100`}
    }
    .flexlayout__tab_button:hover .flexlayout__tab_button_trailing {
        ${tw`opacity-70 hover:opacity-100`}
    }
    .flexlayout__tab_button--selected .flexlayout__tab_button_trailing {
        ${tw`opacity-70 hover:opacity-100`}
    }

    .flexlayout__tab_button_overflow {
        ${tw`ml-2 pl-4 text-sm text-midnight-600`}
    }
    .flexlayout__tab_toolbar {
        ${tw`flex items-center`}
    }
    .flexlayout__tab_toolbar_button {
        ${tw`h-full pt-0 pr-1 pb-0 pl-2 border-none outline-none`}
    }
    .flexlayout__tab_toolbar_sticky_buttons_container {
        ${tw`flex items-center`}
    }
    .flexlayout__tab_floating {
        ${tw`flex absolute overflow-auto bg-red-400 justify-center items-center`}
    }
    .flexlayout__tab_floating_inner {
        ${tw`flex flex-col justify-center items-center overflow-auto`}
    }
    .flexlayout__tab_floating_inner div {
        ${tw`mb-2 text-center`}
    }
    .flexlayout__tab_floating_inner div a {
        ${tw`text-green-400`}
    }
    .flexlayout__border {
        ${tw`flex overflow-hidden bg-red-400`}
    }
    .flexlayout__border_top {
        ${tw`border border-b border-red-400 items-center`}
    }
    .flexlayout__border_bottom {
        ${tw`border border-t border-red-400 items-center`}
    }
    .flexlayout__border_left {
        ${tw`flex flex-col border-r border-red-400 items-center`}
    }
    .flexlayout__border_right {
        ${tw`flex flex-col border-l border-red-400 items-center`}
    }
    .flexlayout__border_inner {
        ${tw`relative flex flex-grow overflow-hidden`}
    }
    .flexlayout__border_inner_tab_container {
        ${tw`absolute flex top-0 bottom-0 [width:'10000px'] whitespace-nowrap`}
    }
    .flexlayout__border_inner_tab_container_right {
        ${tw`origin-top-left [transform:'rotate(90deg)']`}
    }
    .flexlayout__border_inner_tab_container_left {
        ${tw`flex-row-reverse origin-top-right [transform:'rotate(-90deg)']`}
    }
    .flexlayout__border_button {
        ${tw`flex items-center cursor-pointer py-1 px-4 m-1 whitespace-nowrap bg-red-400`}
    }
    .flexlayout__border_button--selected {
        ${tw`bg-red-400 text-green-400`}
    }
    @media (hover: hover) {
        .flexlayout__border_button:hover {
            ${tw`bg-red-200 text-green-400`}
        }
    }
    .flexlayout__border_button--unselected {
        ${tw`text-green-100`}
    }
    .flexlayout__border_button_leading {
        ${tw`inline`}
    }
    .flexlayout__border_button_content {
        ${tw`inline-block`}
    }
    .flexlayout__border_button_trailing {
        ${tw`inline-block ml-5 w-5 h-5`}
    }
    @media (hover: hover) {
        .flexlayout__border_button:hover .flexlayout__border_button_trailing {
            background: transparent url('./images/close.png') no-repeat center;
        }
    }
    .flexlayout__border_button--selected .flexlayout__border_button_trailing {
        background: transparent url('./images/close.png') no-repeat center;
    }
    .flexlayout__border_toolbar {
        ${tw`flex items-center`}
    }
    .flexlayout__border_toolbar_left {
        ${tw`flex-col`}
    }
    .flexlayout__border_toolbar_right {
        ${`flex-col`}
    }
    .flexlayout__border_toolbar_button {
        ${tw`w-5 h-5 border-none outline-none`}
    }
    .flexlayout__border_toolbar_button-float {
        background: transparent url('./images/popout.png') no-repeat center;
    }
    .flexlayout__border_toolbar_button_overflow {
        ${tw`border-none pl-4 text-gray-400`}
        background: transparent url('./images/more2.png') no-repeat left;
    }
    .flexlayout__border_toolbar_button_overflow_top,
    .flexlayout__border_toolbar_button_overflow_bottom {
        ${tw`ml-3`}
    }
    .flexlayout__border_toolbar_button_overflow_right,
    .flexlayout__border_toolbar_button_overflow_left {
        ${tw`mt-2`}
    }
    .flexlayout__popup_menu {
        ${tw`text-sm`}
    }
    .flexlayout__popup_menu_item {
        ${tw`px-2 py-1 hover:bg-gray-200 whitespace-nowrap`}
    }
    .flexlayout__popup_menu_container {
        ${tw`
            absolute bg-gray-100 border rounded border-gray-300
            [transform:'translate(0px, 24px)']
            [z-index:'1000']
            [max-height:'50%']
            [min-width:'100px']
            overflow-auto
        `}
    }
    .flexlayout__floating_window _body {
        ${tw`h-full`}
    }
    .flexlayout__floating_window_content {
        ${tw`absolute inset-0`}
    }
    .flexlayout__floating_window_tab {
        ${tw`absolute inset-0 overflow-auto bg-white text-black`}
    }
    .flexlayout__error_boundary_container {
        ${tw`absolute flex inset-0 content-center`}
    }
    .flexlayout__error_boundary_content {
        ${tw`flex items-center`}
    }
    .flexlayout__tabset_sizer {
        ${tw`pt-2 pb-1`}
    }
    .flexlayout__tabset_header_sizer {
        ${tw`pt-1 pb-1`}
    }
    .flexlayout__border_sizer {
        ${tw`pt-2 pb-2`}
    }
`;

export default Styles;
