from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ice_missing = fields.Boolean(
        compute="_compute_ice_missing",
        store=True,
    )

    @api.depends(
        "partner_id",
        "partner_id.company_registry",
        "partner_id.country_id",
    )
    def _compute_ice_missing(self):
        for rec in self:
            rec.ice_missing = (
                rec.partner_id.country_code == "MA"
                and not rec.partner_id.company_registry
            )

    def _check_ice_before_proceed(self):
        for rec in self:
            if rec.ice_missing:
                raise ValidationError(
                    "Le code ICE du client est obligatoire pour cette "
                    "opération.\nVeuillez renseigner le champ ICE "
                    "(Identifiant Commun de l'Entreprise) dans la fiche "
                    "du client \"%s\" avant de continuer."
                    % rec.partner_id.display_name
                )

    def request_validation(self):
        self._check_ice_before_proceed()
        return super().request_validation()

    def action_confirm(self):
        self._check_ice_before_proceed()
        return super().action_confirm()
