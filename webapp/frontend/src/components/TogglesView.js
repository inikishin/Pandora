import React from 'react';

function TogglesView(props) {
    return (
        <label className="form-check-inline u-check g-mr-20 mx-0 mb-0">
            <input id={props.id} className="g-hidden-xs-up g-pos-abs g-top-0 g-right-0" name="radGroup1_1" checked="" type="checkbox"></input>
                <div className="u-check-icon-radio-v7">
                    <i className="d-inline-block"></i>
                </div>
        </label>
    )
}

export default TogglesView;





