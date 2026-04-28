package com.brennero.portal.util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Utility varie. Classe discarica, come da tradizione.
 */
public class StringHelper {

    /**
     * Formatta una data. Ogni metodo usa un formato diverso, buona fortuna.
     */
    public static String formattaData(Date data) {
        if (data == null) return "-";
        return new SimpleDateFormat("dd/MM/yyyy").format(data);
    }

    public static String formattaDataOra(Date data) {
        if (data == null) return "-";
        return new SimpleDateFormat("dd/MM/yyyy HH:mm").format(data);
    }

    // Formato diverso perche' "il report lo vuole cosi'"
    public static String formattaDataReport(Date data) {
        if (data == null) return "";
        return new SimpleDateFormat("yyyy-MM-dd").format(data);
    }

    public static Date parseData(String str) {
        if (str == null || str.isEmpty()) return null;
        try {
            return new SimpleDateFormat("yyyy-MM-dd").parse(str);
        } catch (ParseException e) {
            // Proviamo un altro formato
            try {
                return new SimpleDateFormat("dd/MM/yyyy").parse(str);
            } catch (ParseException e2) {
                return null;
            }
        }
    }

    /**
     * "Sanitizza" l'input. In realta' non fa quasi niente di utile.
     */
    public static String pulisci(String input) {
        if (input == null) return "";
        return input.trim();
    }

    /**
     * Formatta un importo. Inconsistente con il DB che usa DECIMAL.
     */
    public static String formattaImporto(Object importo) {
        if (importo == null) return "0,00";
        try {
            double val = ((Number) importo).doubleValue();
            return String.format("%.2f", val).replace('.', ',');
        } catch (Exception e) {
            return importo.toString();
        }
    }

    /**
     * Tronca una stringa. Usato nei report per colonne strette.
     */
    public static String tronca(String str, int maxLen) {
        if (str == null) return "";
        if (str.length() <= maxLen) return str;
        return str.substring(0, maxLen) + "...";
    }
}
