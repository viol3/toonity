#region License

using UnityEngine;

namespace BermudaMeshSimplifier
{
    [AddComponentMenu("")]
    internal class LODBackupComponent : MonoBehaviour
    {
        [SerializeField]
        private Renderer[] originalRenderers = null;

        public Renderer[] OriginalRenderers
        {
            get { return originalRenderers; }
            set { originalRenderers = value; }
        }
    }
}
