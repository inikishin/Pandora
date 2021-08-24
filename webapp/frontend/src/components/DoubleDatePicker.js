import React from 'react';

import DatePicker from "./DatePicker";

function DoubleDatePicker(props) {
    return (

        <div class="g-brd-around g-brd-gray-light-v7 g-rounded-4 g-pa-15 g-pa-20--md g-mb-30">
            <h3 class="d-flex align-self-center text-uppercase g-font-size-12 g-font-size-default--md g-color-black g-mb-20">Pick dates</h3>

            <div class="g-mb-30">
                <h4 class="h6 g-font-weight-600 g-color-black g-mb-20">Date:</h4>
                <DatePicker id="from-date"></DatePicker>
            </div>

            <div class="g-mb-30">
                <h4 class="h6 g-font-weight-600 g-color-black g-mb-20">To date:</h4>
                <DatePicker id="to-date"></DatePicker>
            </div>
        </div>

    )
}

export default DoubleDatePicker;