
function build_transaction_block(txid, cb, highlight_address) {
	var builder = function(result) {
		tx = result;
		if('data' in result)
			tx = result['data'];

		var div = `
			<div class="transactions-row">
				<div class="transaction-header">
					<a href="/tx/` + tx['txid'] + `">` + tx['txid'] + `</a><small><div style="opacity: 0.5;">TXID</div></small>
				</div>
				<div class="transaction-io">
					<div class="inputs"><small><div style="opacity: 0.5;">Inputs</div></small>`;
		
		var totalIn = 0;
		tx['vin'].forEach(function(input) {

			if(input['coinbase'] !== undefined) {
				div += `<div class="input">`;
				div += '<small>Newly Generated + Fees</small>';
			}

			if(input['txid'] !== undefined) {
				$.ajax({url: "/api/tx/" + input['txid'], async: false, success: function(result2) {
					output = result2['data']['vout'][input['vout']];
					if(output['scriptPubKey']['addresses'] !== undefined) {
						var classes = 'input';
						var outaddress = output['scriptPubKey']['addresses'][0];
						if(highlight_address !== undefined) {
							if(outaddress == highlight_address) {
								classes += ' highlight';
							}
						}

						div += `<div class="` + classes + `">`;
						div += '<div><a href="/address/' + outaddress + '">' + outaddress + '</a></div><div>' + output['value'] + ' GASP</div>';
						totalIn += output['value'];
					}
				}});
			}

			div += `</div>`;
		});

		if(totalIn > 0) {
			div += '<small><div style="opacity: 0.5; text-align: right;">' + totalIn + ' GASP Total Input</div></small>';
		}

		div += `</div>
				<div class="direction">
					>
				</div>
				<div class="outputs"><small><div style="opacity: 0.5;">Outputs</div></small>`;
		
		var totalOut = 0;
		tx['vout'].forEach(function(output) {

			if(output['scriptPubKey']['addresses'] !== undefined) {
				var classes = 'output';
				var outaddress = output['scriptPubKey']['addresses'][0];
				if(highlight_address !== undefined) {
					if(outaddress == highlight_address) {
						classes += ' highlight';
					}
				}

				div += `<div class="` + classes + `">`;
				div += '<div><a href="/address/' + outaddress + '">' + outaddress + '</a></div><div>' + output['value'] + ' GASP</div>';
				totalOut += output['value']
				div += `</div>`;
			}
		});

		if(totalOut > 0) {
			div += '<small><div style="opacity: 0.5; text-align: right;">' + totalOut + ' GASP Total Output</div></small>';
		}

		var fee = Number((totalIn - totalOut).toFixed(8));
		if(fee > 0) {
			div += '<small><div style="opacity: 0.5; text-align: right;">' + fee + ' GASP Fees Paid</div></small>';
		}

		div += `</div>
				</div>
				<div class="transaction-footer">
				<small><div style="opacity: 0.5;">Processed ` + timeDifference(tx['time']) + `</div></small>
				</div>
			</div>`;

		cb(div);
	}

	if (txid.constructor == Object) {
		builder(txid);
	} else {
		$.ajax({url: "/api/tx/" + txid, success: builder});
	}
}


function assetMutator(value, data, type, params, component) {
	if(data['asset_longname'] !== undefined && data['asset_longname'] != null)
		return data['asset_longname'];
	return value;
}

function assetFormatter(cell, formatterParams, onRendered) {
    if(cell.getValue() == "GASP" || cell.getValue() == "ASP"){
    	return cell.getValue();
    }
	return "<a href=\"/asset/" + cell.getValue() + "\">" + cell.getValue() + "</a>";
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function quantityFormattor(divisible) {
	return function(value, data) {
		var v = value;
		if(Number.isInteger(v)) {
		} else {
			v = v.getValue();
		}
		if(divisible) {
			var q = (v / 100000000).toString().split('.');
			var r = numberWithCommas(q[0]);
			if(q[1] !== undefined) 
				r += '.' + q[1];
			return r;
		}
		return numberWithCommas(v);
	}
}

function quantityMutator(value, data) {
	var v = value;
	if(Number.isInteger(v)) {
	} else {
		v = v.getValue();
	}
	var divisible = false;
	if(data['divisible'] !== undefined) {
		divisible = data['divisible'];
	} else if(data['asset_info'] !== undefined) {
		divisible = data['asset_info']['divisible']
	} else {
		console.log('Not sure how to get divisible...', data);
	}
	if(divisible) {
		var q = (v / 100000000).toString().split('.');
		var r = numberWithCommas(q[0]);
		if(q[1] !== undefined) 
			r += '.' + q[1];
		return r;
	}
	return numberWithCommas(v);
}
