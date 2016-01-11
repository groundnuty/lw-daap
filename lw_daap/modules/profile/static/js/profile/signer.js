/*
 * This file is part of Lifewatch DAAP.
 * Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
 *
 * Lifewatch DAAP is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Lifewatch DAAP is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * This code is taken almost directly from webfts
 * See https://github.com/cern-it-sdc-id/webfts
 */


define(function(require) {
    'use strict';

    require([
        'js/profile/asn11',
        'vendors/asn1js/hex',
        'vendors/asn1js/base64',
        '/vendors/jsrsasign/jsrsasign-latest-all-min.js'
    ], function() {});

    return signRequest;

    function getUTCDate(time) {
        return time.getUTCFullYear().toString().substring(2, 4)
                        + ("0" + (time.getUTCMonth() + 1).toString()).slice(-2)
                        + ("0" + time.getUTCDate().toString()).slice(-2)
                        + ("0" + time.getUTCHours().toString()).slice(-2)
                        + ("0" + time.getUTCMinutes().toString()).slice(-2)
                        + ("0" + time.getUTCSeconds().toString()).slice(-2)
                        + "Z";
    }

    function getSubjectKeyIdentifier(der) {
            var asn1 = ASN11.decode(der);
            var dom = asn1.toDOM();
            return getSKID(dom, "2.5.29.14");
    };

    function getSKID(dom, skid){
            if (dom.textContent.indexOf(skid) > -1){
                    var n = dom.textContent.indexOf(skid);
                    var n2 = dom.textContent.indexOf(skid, n+1);
                    //Output should be like:
                    //2.5.29.35authorityKeyIdentifierX.509 extensionOCTET STRING(1 elem)Offset: 654Length: 2+24(encapsulates)Value:(1 elem)SEQUENCE(1 elem)Offset: 656Length: 2+22(constructed)Value:(1 elem)[0](20 byte) 98CC92D04630368CB0ED980D7251A9474CAABE21
                    var ext = dom.textContent.substring(n2, n2 + 300);
                    var n3 = ext.indexOf("20 byte");
                    return ext.substring(n3 + 9, n3 + 49);
            }
            if (dom.childNodes.length > 0){
                    for (var i=0; i<dom.childNodes.length; i++){
                            getAKI(dom.childNodes[i]);
                    }
            }
    }

    // aeonium: this is here to enforce SHA256 signing
    function sign(cert) {
        cert.asn1SignatureAlg = cert.asn1TBSCert.asn1SignatureAlg;

        var sig = new KJUR.crypto.Signature({'alg': 'SHA256withRSA'});
        sig.init(cert.prvKey);
        sig.updateHex(cert.asn1TBSCert.getEncodedHex());
        cert.hexSig = sig.sign();

        cert.asn1Sig = new KJUR.asn1.DERBitString({'hex': '00' + cert.hexSig});

        var seq = new KJUR.asn1.DERSequence({'array': [cert.asn1TBSCert,
                                                       cert.asn1SignatureAlg,
                                                       cert.asn1Sig]});
        cert.hTLV = seq.getEncodedHex();
        cert.isModified = false;
    };


    function signRequest(sCert, userPrivateKeyPEM, userCERT) {
        var defaultProxyHours = 12;
        var reHex = /^\s*(?:[0-9A-Fa-f][0-9A-Fa-f]\s*)+$/;



        // aeonium: put this here, otherwise YAHOO is not found :(
        var ProxyInfo = function(params) {
            ProxyInfo.superclass.constructor.call(this, params);

            this.setInfoArray = function(info) {
                this.asn1ExtnValue = new KJUR.asn1.DERSequence();
                if (typeof info['pathlen'] != "undefined") {
                    var o = new KJUR.asn1.DERInteger(info['pathlen']);
                    this.asn1ExtnValue.appendASN1Object(o);
                }
                if (typeof info['policy'] != "undefined") {
                    var pcySeq = new KJUR.asn1.DERSequence();
                    var o = new KJUR.asn1.DERObjectIdentifier(info['policy'])
                    pcySeq.appendASN1Object(o);
                    this.asn1ExtnValue.appendASN1Object(pcySeq);
                }
            };

            this.getExtnValueHex = function() {
                return this.asn1ExtnValue.getEncodedHex();
            };

            this.oid = '1.3.6.1.5.5.7.1.14';
            if (typeof params != "undefined") {
                if (typeof params['info'] != "undefined") {
                    this.setInfoArray(params['info']);
                }
            }
        };
        YAHOO.lang.extend(ProxyInfo, KJUR.asn1.x509.Extension);

        try {
            var derServer = reHex.test(sCert) ? Hex.decode(sCert) : Base64
                    .unarmor(sCert);

            var derUser = reHex.test(userCERT) ? Hex.decode(userCERT) : Base64
                    .unarmor(userCERT);

            var asn1 = ASN11.decode(derServer);
            var pos = asn1.getCSRPubKey();
            //console.log(sCert);

            // aeonium: try to get the subject string...
            X509.DN_ATTRHEX['060a0992268993f22c640119'] = "DC";
            var ct = new X509();
            ct.readCertPEM(userCERT);
            var userDN = ct.getSubjectString()
            var oIssuer = ct.getIssuerHex();
            var oSerial = Math.floor(Math.random() * 6553600) + 6553600;
            console.log(oIssuer);
            // FIXME: use a better value here
            var subject = userDN + '/CN=' + oSerial;
            console.log(subject);

            var rsakey = new RSAKey();
            //The replace is because other wise something like this was
            //found "01 00 01" and only the last part, "01", was converted.
            //It was returning 1 instead of 65537
            rsakey.setPublic(pos.modulus.replace(/ /g, ''), pos.exponent.replace(/ /g, ''));

            // TODO: verify sign
            var tbsc = new KJUR.asn1.x509.TBSCertificate();

            // Time
            tbsc.setSerialNumberByParam({
                'int' : oSerial
            });
            tbsc.setSignatureAlgByParam({
                'name' : 'SHA256withRSA'
            });
            tbsc.setIssuerByParam({
                'str' : userDN
            });

            tbsc.asn1Issuer.hTLV = ct.getSubjectHex();

            tbsc.setSubjectByParam({
                'str' : subject
            });
            // Public key from server (from CSR)
            tbsc.setSubjectPublicKeyByParam({
                'rsakey' : rsakey
            });

            var ctime = new Date();
            ctime.setUTCHours(ctime.getUTCHours() - 1);
            tbsc.setNotBeforeByParam({
                'str' : getUTCDate(ctime)
            });
            ctime.setUTCHours(ctime.getUTCHours() + 1 + defaultProxyHours);
            tbsc.setNotAfterByParam({
                'str' : getUTCDate(ctime)
            });

            //tbsc.appendExtension(new KJUR.asn1.x509.BasicConstraints({'cA': false, 'critical': true}));
            // 1011 to set 'Digital Signature, Key Encipherment, Data Encipherment'. 0 means disabled 'Non Repudiation'
            tbsc.appendExtension(new KJUR.asn1.x509.KeyUsage({'bin':'1011', 'critical':true}));

            var s = KEYUTIL.getPEM(rsakey);
            var sHashHex = getSubjectKeyIdentifier(derUser);
            var paramAKI = {'kid': {'hex': sHashHex }, 'issuer': oIssuer, 'critical': false};
            //tbsc.appendExtension(new KJUR.asn1.x509.AuthorityKeyIdentifier(paramAKI));

            // AEONIUM: RFC 3820 Proxy Info
            var paramPI = {
                'critical': true,
                'info': {
                    // inherit all, no pathlen
                    'policy': {'oid': '1.3.6.1.5.5.7.21.1'}
                }
            }
            tbsc.appendExtension(new ProxyInfo(paramPI));


            // Sign and get PEM certificate with CA private key
            var userPrivateKey = new RSAKey();

            // The private RSA key can be obtained from the p12 certificate by using:
            // openssl pkcs12 -in yourCert.p12 -nocerts -nodes | openssl rsa
            userPrivateKey.readPrivateKeyFromPEMString(userPrivateKeyPEM);

            var cert = new KJUR.asn1.x509.Certificate({
                'tbscertobj' : tbsc,
                'rsaprvkey' : userPrivateKey,
                'prvkey' : userPrivateKey,
                'rsaprvpas' : "empty"
            });

            // TODO check times in all certificates involved to check that the
            // expiration in the
            // new one is not later than the others
            sign(cert);

            var pemCert = cert.getPEMString();
            //console.log(pemCert.replace(/^\s*$[\n\r]{1,}/gm, "\n"));

            //In case blank new lines...
            return pemCert.replace(/^\s*$[\n\r]{1,}/gm, "\n");
        } catch (e) {
            console.log("ERROR signing the CSR response: " + e);
        }
    }
});
