import React from 'react';
import ReactDOM from 'react-dom';

class QuotesLoader extends React.Component {
    constructor(props) {
        super(props);
        this.state = {id: null,
                        status: 'READY'};

        // Привязка необходима, чтобы сделать this доступным в коллбэке
        this.startLoad = this.startLoad.bind(this);
        this.checkStatus = this.checkStatus.bind(this);
    }

    startLoad() {
        fetch('http://localhost:9999/api/loadquotes')
            .then(response => response.json())
            .then(result => this.setState(
                {id: result.id,
                      status: 'PENDING'
                      }
                )
            )

        this.checkerID = setInterval(() => this.checkStatus(), 3000);
    }


    checkStatus(){
        fetch('http://localhost:9999/api/getaskstatus/' + this.state.id)
            .then(response => response.json())
            .then(result => {
                if (result.is_ready) {
                    clearInterval(this.checkerID);
                    this.setState({id: null,
                      status: 'READY'
                      });
                }
            })

    }

    render() {
        return (
            <div>
                <p>Текущий статус: {this.state.status}</p>
                <button onClick={this.startLoad}>Load</button>
                <button onClick={this.checkStatus}>Check status</button>
                <h3>{this.state.id}</h3>
            </div>
        );
    }

}

export default QuotesLoader;