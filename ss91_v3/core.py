#!/usr/bin/env python3
from .sher_adapter import SherAdapter
from .risk import calc_stop_loss, calc_take_profit

class SS91Core:
    def __init__(self, sher_model_path=None, conf_threshold=0.75):
        self.sher = SherAdapter(model_path=sher_model_path)
        self.conf_threshold = conf_threshold

    def decide(self, factors_snapshot: dict, price_now: float, atr_now: float, atr_ma: float):
        # flatten features expected by Sherloock
        features = {}
        for k,v in factors_snapshot.items():
            if isinstance(v, dict) and v.get('value') is not None:
                features[k] = v['value']
            elif isinstance(v,(int,float)):
                features[k] = v
            else:
                features[k] = 0.0
        features['price_now'] = price_now
        features['atr_now'] = atr_now
        features['atr_ma'] = atr_ma

        out = self.sher.predict(features)
        signal = out.get('signal','HOLD')
        conf = out.get('confidence',0.0)
        meta = out.get('meta',{})

        result = {"signal":signal,"confidence":conf,"meta":meta}
        # gates
        if conf < self.conf_threshold:
            result['decision'] = 'HOLD:low_conf'
            return result
        if atr_now is None or atr_ma is None or atr_now <= atr_ma:
            result['decision'] = 'HOLD:low_atr'
            return result
        if signal not in ['BUY','SELL']:
            result['decision'] = 'HOLD'
            return result

        entry = price_now
        wave1 = meta.get('wave1_size', atr_now*10)
        sl = calc_stop_loss(entry, atr_now, signal)
        tp1 = calc_take_profit(entry, wave1, signal)
        result.update({"decision":f"EXEC_{signal}","sl":sl,"tp1":tp1})
        return result
