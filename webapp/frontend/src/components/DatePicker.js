import React from 'react';

function DatePicker(props) {
    return (
        <div id="datepickerWrapper" className="u-datepicker-right u-datepicker--v3 g-pos-rel w-100 g-cursor-pointer g-brd-around g-brd-gray-light-v7 g-rounded-4">
            <input id={props.id} className="js-range-datepicker w-100 g-bg-transparent g-font-size-12 g-font-size-default--md g-color-gray-dark-v6 g-pr-80 g-pl-15 g-py-9"
                   type="text" placeholder="Select Date" data-rp-wrapper="#datepickerWrapper" data-rp-date-format="d/m/Y"></input>
                <div className="d-flex align-items-center g-absolute-centered--y g-right-0 g-color-gray-light-v6 g-color-lightblue-v9--sibling-opened g-mr-15">
                    <i className="hs-admin-calendar g-font-size-18 g-mr-10"></i>
                    <i className="hs-admin-angle-down"></i>
                </div>
        </div>
        );
    }

export default DatePicker;